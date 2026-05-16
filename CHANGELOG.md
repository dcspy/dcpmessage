# Changelog

All notable changes to this project will be documented in this file.

## [1.3.2] - 2026-05-16
### Fixed
- Fixed `ServerError.is_end_of_message` shadowing method with boolean instance attribute (now a `@property`)
- Fixed `DcpMessageSource.GOES` (value=0) unable to be added as a source due to deduplication check
- Fixed `SearchCriteria.__eq__` not comparing `sources` field
- Fixed mixed line endings in `SearchCriteria.__str__` (now consistently `\n`)
- Fixed socket connection leak in `DcpMessage.get()` if `request_dcp_blocks()` raises
- Replaced `assert` statements with proper `ProtocolError` exceptions in message parsing
- Removed unused methods `LddsMessage.is_end_of_message()` and `LddsMessage.is_success()`

### Changed
- Removed unnecessary `@dataclass` decorators from `LddsMessageConstants` and `LddsMessageIds`
- Simplified `LddsClient._wrap_tls()` exception handling
- Removed redundant `try/except/raise` in `LddsClient.request_dcp_blocks()`
- Improved error messaging for sources exceeding max limit

## [1.3.0] - 2025-07-16
### Added
- Enable use of TLS.