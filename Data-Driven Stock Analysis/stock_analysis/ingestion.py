"""Load nested market YAML, normalize daily OHLCV rows, and report data issues."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

FIELD_ALIASES = {
    "symbol": ("symbol", "ticker", "stock", "stock_symbol", "tradingsymbol"),
    "date": ("date", "trade_date", "trading_date", "timestamp"),
    "open": ("open", "open_price"),
    "high": ("high", "high_price"),
    "low": ("low", "low_price"),
    "close": ("close", "close_price", "closing_price", "closing", "adj_close", "adjusted_close"),
    "volume": ("volume", "traded_volume", "total_traded_quantity"),
}
REQUIRED_FIELDS = ("symbol", "date", "open", "high", "low", "close", "volume")
MONTH_NAMES = {
    name.lower(): index for index, name in enumerate(
        ("January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"), start=1
    )
}
DATE_KEY = re.compile(
    r"^(?:\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|"
    r"\d{1,2}[- ][A-Za-z]{3}[- ]\d{4}|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},?\s+\d{4})$",
    re.IGNORECASE,
)
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_YAML_FILES = 5000


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def _field_map(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {_key(key): value for key, value in record.items()}
    result = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if _key(alias) in normalized:
                result[field] = normalized[_key(alias)]
                break
    return result


def _is_symbol_key(value: Any) -> bool:
    text = str(value).strip()
    if not text or DATE_KEY.match(text):
        return False
    if text.lower() in MONTH_NAMES or text.lower() in {"data", "stocks", "prices", "records", "symbol", "ticker"}:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9&._-]{0,24}", text))


def _records(node: Any, path: tuple[str, ...] = ()):
    if isinstance(node, dict):
        fields = _field_map(node)
        if any(field in fields for field in (*REQUIRED_FIELDS, "close")):
            yield fields, path
        for key, value in node.items():
            yield from _records(value, path + (str(key),))
    elif isinstance(node, list):
        for item in node:
            yield from _records(item, path)


def _context_symbol(path: tuple[str, ...]) -> str | None:
    for value in reversed(path):
        if _is_symbol_key(value) and not re.fullmatch(r"\d+", value):
            return value
    return None


def _context_date(path: tuple[str, ...]) -> Any:
    for value in reversed(path):
        text = value.strip()
        if DATE_KEY.match(text):
            return text
    return None


def _as_frame(raw_records: list[dict[str, Any]]) -> pd.DataFrame:
    if not raw_records:
        return pd.DataFrame(columns=REQUIRED_FIELDS)
    frame = pd.DataFrame(raw_records)
    for field in REQUIRED_FIELDS:
        if field not in frame:
            frame[field] = pd.NA
    return frame[list(REQUIRED_FIELDS)]


def _parse_date(value: Any) -> pd.Timestamp:
    if pd.isna(value):
        return pd.NaT
    text = re.sub(r"(?<=\d)(?:st|nd|rd|th)\b", "", str(value).strip(), flags=re.IGNORECASE)
    day_first = not bool(re.match(r"^\d{4}[-/]", text))
    return pd.to_datetime(text, errors="coerce", dayfirst=day_first)


def normalize_records(document: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Normalize nested YAML rows and return clean OHLCV data plus a report."""
    extracted = []
    for fields, path in _records(document):
        row = dict(fields)
        if not row.get("symbol"):
            row["symbol"] = _context_symbol(path)
        if not row.get("date"):
            row["date"] = _context_date(path)
        if any(field in row for field in ("open", "high", "low", "close", "volume")):
            extracted.append(row)

    frame = _as_frame(extracted)
    report: dict[str, Any] = {
        "records_found": len(frame),
        "accepted_rows": 0,
        "rejected_rows": 0,
        "duplicate_rows_removed": 0,
        "rejection_reasons": {},
    }
    if frame.empty:
        return frame, report

    frame["symbol"] = frame["symbol"].astype("string").str.strip().str.upper()
    frame["date"] = frame["date"].map(_parse_date).dt.normalize()
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(
            frame[column].astype("string").str.replace(",", "", regex=False).str.replace(r"[$₹]", "", regex=True),
            errors="coerce",
        )

    checks = {
        "missing_symbol": frame["symbol"].isna() | frame["symbol"].eq(""),
        "invalid_date": frame["date"].isna(),
        "invalid_price_or_volume": frame[["open", "high", "low", "close", "volume"]].isna().any(axis=1),
        "non_positive_price": frame[["open", "high", "low", "close"]].le(0).any(axis=1),
        "negative_volume": frame["volume"].lt(0),
        "inconsistent_high_low": frame["high"].lt(frame[["open", "low", "close"]].max(axis=1))
        | frame["low"].gt(frame[["open", "high", "close"]].min(axis=1)),
    }
    invalid = pd.Series(False, index=frame.index)
    for reason, mask in checks.items():
        report["rejection_reasons"][reason] = int(mask.sum())
        invalid |= mask
    clean = frame.loc[~invalid].copy()
    before_dedup = len(clean)
    clean = clean.drop_duplicates(["symbol", "date"], keep="last")
    report["duplicate_rows_removed"] = before_dedup - len(clean)
    report["rejected_rows"] = int(invalid.sum())
    report["accepted_rows"] = len(clean)
    clean = clean.sort_values(["symbol", "date"]).reset_index(drop=True)
    return clean, report


def load_yaml(path: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read one YAML file or a ZIP of YAML files and normalize the observations."""
    source = Path(path)
    if source.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(source) as archive:
                yaml_members = sorted(
                    (member for member in archive.infolist()
                     if not member.is_dir() and member.filename.lower().endswith((".yaml", ".yml"))),
                    key=lambda member: member.filename,
                )
                if not yaml_members:
                    raise ValueError(f"No YAML files found in stock data archive: {source}")
                if len(yaml_members) > MAX_ARCHIVE_YAML_FILES:
                    raise ValueError(
                        f"Stock archive contains too many YAML files ({len(yaml_members)}; "
                        f"limit is {MAX_ARCHIVE_YAML_FILES})."
                    )
                total_size = sum(member.file_size for member in yaml_members)
                if total_size > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        f"Stock archive expands to {total_size:,} bytes; "
                        f"limit is {MAX_ARCHIVE_UNCOMPRESSED_BYTES:,} bytes."
                    )
                documents = []
                for member in yaml_members:
                    try:
                        documents.append(yaml.safe_load(archive.read(member)))
                    except yaml.YAMLError as error:
                        raise ValueError(f"Invalid YAML in archive member {member.filename}: {error}") from error
                document = [
                    record
                    for part in documents
                    if part is not None
                    for record in (part if isinstance(part, list) else [part])
                ]
        except zipfile.BadZipFile as error:
            raise ValueError(f"Stock data archive is not a valid ZIP file: {source}") from error
    else:
        with source.open("r", encoding="utf-8-sig") as file:
            document = yaml.safe_load(file)
    data, report = normalize_records(document)
    report["source"] = str(source)
    if source.suffix.lower() == ".zip":
        report["source_files"] = len(yaml_members)
    if data.empty:
        raise ValueError(
            "No valid OHLCV rows were found. Each observation needs symbol, date, "
            "open, high, low, close, and volume fields (or equivalent nested keys)."
        )
    return data, report


def find_yaml(directory: str | Path) -> Path | None:
    """Find the preferred YAML or stock ZIP input in the raw-data directory."""
    root = Path(directory)
    for candidate in (
        root / "stock_dataset.yaml",
        root / "stock_dataset.yml",
        root / "stock_dataset.zip",
    ):
        if candidate.is_file():
            return candidate
    matches = sorted([*root.glob("*.yaml"), *root.glob("*.yml")])
    if matches:
        return matches[0]
    archives = sorted(root.glob("*.zip"))
    return archives[0] if archives else None


def load_sectors(path: str | Path | None) -> pd.DataFrame:
    """Load an optional symbol-to-sector CSV; an empty frame means unmapped."""
    columns = ["symbol", "sector"]
    if path is None or not Path(path).is_file():
        return pd.DataFrame(columns=columns)
    sectors = pd.read_csv(path)
    normalized = {_key(column): column for column in sectors.columns}
    symbol_col = next((normalized[name] for name in ("symbol", "ticker", "stock_symbol") if name in normalized), None)
    sector_col = next((normalized[name] for name in ("sector", "industry") if name in normalized), None)
    if symbol_col is None or sector_col is None:
        raise ValueError("Sector CSV must have `symbol` and `sector` columns.")
    result = sectors[[symbol_col, sector_col]].copy()
    result.columns = columns
    result["symbol"] = result["symbol"].astype("string").str.strip().str.upper()
    result["sector"] = result["sector"].astype("string").str.strip()
    result = result.dropna().drop_duplicates("symbol", keep="last")
    return result[result["sector"].ne("")]
