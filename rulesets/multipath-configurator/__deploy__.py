
name = "multipath-configurator"

add_files = (
    "ruleset.py",
)

add_modules = True  # find modules in directory (folders having __init__.py file) and add them to container

extra_commands = (
#    ("RUN", "pip install my-wonderful-lib==1.0"),
)

labels = {
    "serving.knative.dev/visibility": "cluster-local",
    "krules.airspot.dev/type": "ruleset",
    "krules.airspot.dev/ruleset": name
}

template_annotations = {
    "autoscaling.knative.dev/minScale": "1",
}

service_account = "demo-serviceaccount"

triggers = (
   {
       "name": "on-multus-app-change",
       "filter": {
           "attributes": {
               "type": "subject-property-changed",
               "multusapp": "firewall",
           }
       }
   },
   {
       "name": "on-fw-delete",
       "filter": {
           "attributes": {
               "type": "fw-delete",
               "multusapp": "firewall",
           }
       }
   }
)
triggers_default_broker = "default"

ksvc_sink = "broker:default"
ksvc_procevents_sink = "broker:procevents"

