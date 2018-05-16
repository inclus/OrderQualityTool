from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

dhis2_settings = Section("DHIS2_Settings")


@global_preferences_registry.register
class DHIS2_URL(StringPreference):
    section = dhis2_settings
    verbose_name = "DHIS2 URL"
    name = "DHIS2_URL"
    default = "http://localhost:8080"


@global_preferences_registry.register
class DHIS2_USERNAME(StringPreference):
    section = dhis2_settings
    verbose_name = "DHIS2 USERNAME"
    name = "DHIS2_USERNAME"
    default = "admin"


@global_preferences_registry.register
class DHIS2_PASSWORD(StringPreference):
    section = dhis2_settings
    verbose_name = "DHIS2 PASSWORD"
    name = "DHIS2_PASSWORD"
    default = "district"
