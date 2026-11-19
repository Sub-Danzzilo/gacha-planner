# Tests for storage/serializers.py and storage/profile_repository.py. Phase 1.
#
# Use pytest's tmp_path; never touch data/profiles/.
#
# Cases:
#   - save then load returns an equal profile (banners with each rate curve type, Decimal
#     amounts preserved exactly)
#   - atomic write: a failure while writing does not corrupt an existing file
#   - unknown schema_version raises StorageError
#   - missing or wrongly typed field raises StorageError naming the field
#   - profile names that try to escape the directory are rejected
#   - list_profiles, exists and delete behave as documented
