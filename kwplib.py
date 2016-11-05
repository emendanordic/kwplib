import collections, logging, os, re, sys
import socket
if sys.version_info >= (3, 0):
    import urllib.parse
    import urllib.request
else:
    import httplib, urllib, urllib2

RE_URL_PATTERN = "^(http[s]?):\/\/([\w.]+)*:([0-9]+)"
RE_API_PATTERN = "^(http[s]?):\/\/([\w.]+)*:([0-9]+)\/review\/api$"

class KwApiCon:
    def __init__(self, url=None, user=None, verbose=False):
        self.url = None
        self.api = None
        self.host = None
        self.port = None

        self.user = None
        self.ltoken = None

        logLevel = logging.INFO
        if verbose:
            logLevel = logging.DEBUG
        logging.basicConfig(level=logLevel,
            format='%(levelname)s:%(asctime)s %(name)s %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S')
        self.logger = logging.getLogger('kwplib')

        self.set_url(url)
        self.set_user(user)


    def set_url(self, url):
        if url:
            self.url = url
            self.api = url + "/review/api"
            self.logger.debug("Validating URL to api '{0}' with regular expression \
                '{1}'...".format(self.api, RE_API_PATTERN))
            if not (re.match(RE_API_PATTERN, self.api)):
                sys.exit("URL {} does not match required pattern".format(self.api))
            result = re.search(RE_URL_PATTERN, url)
            self.ssl = (result.group(1) == 'https')
            self.host = result.group(2)
            self.port = result.group(3)
            self.get_ltoken_hash()

    def set_user(self, user):
        if user:
            self.user = user
            self.get_ltoken_hash()


    def get_ltoken_hash(self):
        if (self.host != None and self.port != None and self.user != None):
            self.ltoken = self._get_ltoken_hash()


    def _get_ltoken_hash(self):
        ltoken_path = self._get_ltoken_path()
        with open(ltoken_path, 'r') as f:
            for r in f:
                rd = r.strip().split(';')
                if rd[0] == self.host and rd[1] == self.port and rd[2] == self.user:
                    return rd[2]
                else:
                    sys.exit(("Could not find matching ltoken record. Searching for"
                        " host '{0}', port '{1}' and user '{2}' in file '{3}'").format(
                            self.host, self.port, self.user, ltoken_path
                        ))

    # return ltoken file path or None, if not found
    def _get_ltoken_path(self):
        ltoken_path = os.path.join(os.path.expanduser('~'), ".klocwork", "ltoken")
        if not os.path.exists(ltoken_path):
            sys.exit("Could not find ltoken file '{0}'".format(ltoken_path))
        return ltoken_path

    def execute_query(self, values):
        if not self.ltoken:
            sys.exit(("ltoken hash not set. Please ensure you have provided the"
            " url and user"))
        if not 'action' in values:
            sys.exit("No action specified in values '{0}'".format(values))
        values['user'] = self.user
        values['ltoken'] = self.ltoken
        result = self._query(values)
        print result.response

    def _query(self, values):
        QueryResponse = collections.namedtuple('QueryResponse', ['response', 'error_msg'])
        if sys.version_info >= (3, 0):
            data = urllib.parse.urlencode(values).encode("utf-8")
            try:
                response = urllib.request.urlopen(self.api, data)
                return response.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                print('HTTP Connection Error code: ', str(e.read()))
            except urllib.error.URLError as e:
                print('URL Error: ', str(e))
        else:
            data = urllib.urlencode(values)
            request = urllib2.Request(self.api, data)
            try:
                response = urllib2.urlopen(request).read()
                return QueryResponse(response, None)
            except urllib2.HTTPError as e:
                return QueryResponse(None, 'HTTP Connection Error code: ' + str(e.read()))
            except urllib2.URLError as e:
                return QueryResponse(None, 'URL Error: ' +  str(e.reason))
            except httplib.InvalidURL as e:
                return QueryResponse(None, 'Invalid URL Error: ' +  str(e))
            except:
                return QueryResponse(None, 'Error not caught... Something else went wrong.')

    def builds(self, project):
        vals = {"action" : "builds",
                "user" : self.user,
                "project" : project }
        return self._query(vals)

    def create_group(self, name, users=""):
        vals = {"action" : "create_group",
                "user" : self.user,
                "name" : name }
        if users == "users":
            vals["users"] = users
        return self._query(vals)

    def create_module(self, project, name, paths, allow_all="", allow_users="", allow_groups="", \
            deny_users="", deny_groups="", tags=""):
        vals = {"action" : "create_module",
                "user" : self.user,
                "project" : project,
                "name" : name,
                "paths" : paths}
        if allow_all == "true":
            vals["allow_all"] = "true"
        if not allow_users == "":
            vals["allow_users"] = allow_users
        if not allow_groups == "":
            vals["allow_groups"] = allow_groups
        if not deny_users == "":
            vals["deny_users"] = deny_users
        if not deny_groups == "":
            vals["deny_groups"] = deny_groups
        if not tags == "":
            vals["tags"] = tags
        return self._query(vals)

    def create_role(self, name, create_project="", manage_roles="", manage_users="",
            access_source_files="", assign_role="", change_project_settings="",
            create_build="", delete_build="", delete_project="", manage_modules="",
            use_local_configuration="", change_issue_status="", allowed_status_transitions=""):
        vals = {"action" : "create_role",
                "user" : self.user,
                "name" : name}
        if not create_project == "":
            vals["create_project"] = create_project
        if not manage_roles == "":
            vals["manage_roles"] = manage_roles
        if not manage_users == "":
            vals["manage_users"] = manage_users
        if not access_source_files == "":
            vals["access_source_files"] = access_source_files
        if not assign_role == "":
            vals["assign_role"] = assign_role
        if not change_project_settings == "":
            vals["change_project_settings"] = change_project_settings
        if not create_build == "":
            vals["create_build"] = create_build
        if not delete_build == "":
            vals["delete_build"] = delete_build
        if not delete_project == "":
            vals["delete_project"] = delete_project
        if not manage_modules == "":
            vals["manage_modules"] = manage_modules
        if not use_local_configuration == "":
            vals["use_local_configuration"] = use_local_configuration
        if not change_issue_status == "":
            vals["change_issue_status"] = change_issue_status
        if not allowed_status_transitions == "":
            vals["allowed_status_transitions"] = allowed_status_transitions
        return self._query(vals)

    def create_user(self, name, password=""):
        vals = {"action" : "create_user",
                "user" : self.user,
                "name" : name}
        if not password == "":
            vals["password"] = password
        return self._query(vals)

    def create_view(self, project, name, query, tags="", is_public=""):
        vals = {"action" : "create_view",
                "user" : self.user,
                "project" : project,
                "name" : name}
        if not query == "":
            vals["query"] = query
        if not tags == "":
            vals["tags"] = tags
        if is_public == "true" or is_public == "false":
            vals["is_public"] = is_public
        return self._query(vals)

    def defect_types(self, project):
        vals = {"action" : "defect_types",
                "user" : self.user,
                "project" : project}
        return self._query(vals)

    def delete_build(self, project, name):
        vals = {"action" : "delete_build",
                "user" : self.user,
                "project" : project,
                "name" : name}
        return self._query(vals)

    def delete_group(self, name):
        vals = {"action" : "delete_group",
                "user" : self.user,
                "name" : name}
        return self._query(vals)

    def delete_module(self, project, name):
        vals = {"action" : "delete_module",
                "user" : self.user,
                "project" : project,
                "name" : name}
        return self._query(vals)

    def delete_project(self, name):
        vals = {"action" : "delete_project",
                "user" : self.user,
                "name" : name}
        return self._query(vals)

    def delete_role(self, name):
        vals = {"action" : "delete_role",
                "user" : self.user,
                "name" : name}
        return self._query(vals)

    def delete_user(self, name):
        vals = {"action" : "delete_user",
                "user" : self.user,
                "name" : name}
        return self._query(vals)

    def delete_view(self, project, name):
        vals = {"action" : "delete_view",
                "user" : self.user,
                "project" : project,
                "name" : name}
        return self._query(vals)

    def fchurns(self, project, view="", viewCreator="", latestBuilds="", component=""):
        vals = {"action" : "fchurns",
                "user" : self.user,
                "project" : project}
        if not view == "":
            vals["view"] = view
        if not viewCreator == "":
            vals["viewCreator"] = viewCreator
        if not latestBuilds == "":
            vals["latestBuilds"] = latestBuilds
        if not component == "":
            vals["component"] = component
        return self._query(vals)

    def groups(self, search="", list_users="false", limit=""):
        vals = {"action" : "delete_view",
                "user" : self.user,
                "list_users" : list_users}
        if not search == "":
            vals["search"] = search
        if not limit == "":
            vals["limit"] = limit
        return self._query(vals)

    def import_project(self, project, sourceURL, sourceAdmin, sourcePassword=""):
        vals = {"action" : "import_project",
                "user" : self.user,
                "project" : project,
                "sourceURL" : sourceURL,
                "sourceAdmin" : sourceAdmin}
        if not sourcePassword == "":
            vals["sourcePassword"] = sourcePassword
        return self._query(vals)

    def import_server_configuration(self, sourceURL, sourceAdmin, sourcePassword=""):
        vals = {"action" : "import_project",
                "user" : self.user,
                "sourceURL" : sourceURL,
                "sourceAdmin" : sourceAdmin}
        if not sourcePassword == "":
            vals["sourcePassword"] = sourcePassword
        return self._query(vals)

    def import_status(self):
        vals = {"action" : "import_status",
                "user" : self.user}
        return self._query(vals)

    def issue_details(self, project, id, include_xsync="false"):
        vals = {"action" : "import_status",
                "user" : self.user,
                "project" : project,
                "id" : id,
                "include_xsync" : include_xsync}
        return self._query(vals)

    def license_count(self, feature=""):
        vals = {"action" : "license_count",
                "user" : self.user}
        if not feature == "":
            vals["feature"] = feature
        return self._query(vals)

    def metrics(self, project, query="", view="", limit=""):
        vals = {"action" : "metrics",
                "user" : self.user,
                "project" : project}
        if not query == "":
            vals["query"] = query
        if not view == "":
            vals["view"] = view
        if not limit == "":
            vals["limit"] = limit
        return self._query(vals)

    def modules(self, project):
        vals = {"action" : "modules",
                "user" : self.user,
                "project" : project}
        return self._query(vals)

    def project_configuration(self, project, build=""):
        vals = {"action" : "project_configuration",
                "user" : self.user,
                "project" : project}
        if not build == "":
            vals["build"] = build
        return self._query(vals)

    def projects(self):
        vals = {"action" : "projects",
                "user" : self.user}
        return self._query(vals)

    def report(self, project, build="", filterQuery="", view="", \
            x="", xDrilldown="", y="", yDrilldown=""):
        vals = {"action" : "report",
                "user" : self.user,
                "project" : project}
        if not build == "":
            vals["build"] = build
        if not filterQuery == "":
            vals["filterQuery"] = filterQuery
        if not view == "":
            vals["view"] = view
        if not x == "":
            vals["x"] = x
        if not xDrilldown == "":
            vals["xDrilldown"] = xDrilldown
        if not y == "":
            vals["y"] = y
        if not yDrilldown == "":
            vals["yDrilldown"] = yDrilldown
        return self._query(vals)

    def role_assignments(self, search=""):
        vals = {"action" : "role_assignments",
                "user" : self.user}
        if not search == "":
            vals["search"] = search
        return self._query(vals)

    def roles(self, search=""):
        vals = {"action" : "roles",
                "user" : self.user}
        if not search == "":
            vals["search"] = search
        return self._query(vals)

    def search(self, project, query="", view="", limit=""):
        vals = {"action" : "search",
                "user" : self.user,
                "project" : project}
        if not query == "":
            vals["query"] = query
        if not view == "":
            vals["view"] = view
        if not limit == "":
            vals["limit"] = limit
        return self._query(vals)

    def task_status(self):
        vals = {"action" : "task_status",
                "user" : self.user}
        return self._query(vals)

    def taxonomies(self, project):
        vals = {"action" : "taxonomies",
                "user" : self.user,
                "project" : project}
        return self._query(vals)

    def update_build(self, project, name, new_name="", keepit=""):
        vals = {"action" : "update_build",
                "user" : self.user,
                "project" : project,
                "name" : name}
        if not new_name == "":
            vals["new_name"] = new_name
        if keepit == "true" or keepit == "false":
            vals["keepit"] = keepit
        return self._query(vals)

    def update_defect_type(self, project, code, enabled="", severity=""):
        vals = {"action" : "update_defect_type",
                "user" : self.user,
                "project" : project,
                "code" : code}
        if enabled == "true" or enabled == "false":
            vals["enabled"] = enabled
        if not severity == "":
            vals["severity"] = severity
        return self._query(vals)

    def update_group(self, name, users="", remove_all="false"):
        vals = {"action" : "taxonomies",
                "user" : self.user,
                "name" : name,
                "remove_all" : remove_all}
        if not users == "":
            vals["users"] = users
        return self._query(vals)

    def update_module(self, project, name, new_name="", allow_all="", \
            allow_users="", allow_groups="", deny_users="", deny_groups="", \
            paths="", tags=""):
        vals = {"action" : "update_module",
                "user" : self.user,
                "project" : project,
                "name" : name}
        if not new_name == "":
            vals["new_name"] = new_name
        if allow_all == "true":
            vals["allow_all"] = "true"
        if not allow_users == "":
            vals["allow_users"] = allow_users
        if not allow_groups == "":
            vals["allow_groups"] = allow_groups
        if not deny_users == "":
            vals["deny_users"] = deny_users
        if not deny_groups == "":
            vals["deny_groups"] = deny_groups
        if not paths == "":
            vals["paths"] = paths
        if not tags == "":
            vals["tags"] = tags
        return self._query(vals)

    def update_project(self, name, new_name="", description="", tags=""):
        vals = {"action" : "update_project",
                "user" : self.user,
                "name" : name}
        if not new_name == "":
            vals["new_name"] = new_name
        if not description == "":
            vals["description"] = description
        if not tags == "":
            vals["tags"] = tags
        return self._query(vals)

    def update_role_assignment(self, name, project="", account="", group="", remove="false"):
        vals = {"action" : "version",
                "user" : self.user,
                "name" : name,
                "account" : account,
                "remove" : remove}
        if not project == "":
            vals["project"] = project
        if not remove == "":
            vals["remove"] = remove
        return self._query(vals)

    def update_role_permissions(self, name, create_project="", manage_roles="",
            manage_users="", access_source_files="", assign_role="",
            change_project_settings="", create_build="", delete_build="",
            delete_project="", manage_modules="", use_local_configuration="",
            change_issue_status="", allowed_status_transitions=""):
        vals = {"action" : "version",
                "user" : self.user,
                "name" : name}
        if not create_project == "":
            vals["create_project"] = create_project
        if not manage_roles == "":
            vals["manage_roles"] = manage_roles
        if not manage_users == "":
            vals["manage_users"] = manage_users
        if not access_source_files == "":
            vals["access_source_files"] = access_source_files
        if not assign_role == "":
            vals["assign_role"] = assign_role
        if not change_project_settings == "":
            vals["change_project_settings"] = change_project_settings
        if not create_build == "":
            vals["create_build"] = create_build
        if not delete_build == "":
            vals["delete_build"] = delete_build
        if not delete_project == "":
            vals["delete_project"] = delete_project
        if not manage_modules == "":
            vals["manage_modules"] = manage_modules
        if not use_local_configuration == "":
            vals["use_local_configuration"] = use_local_configuration
        if not change_issue_status == "":
            vals["change_issue_status"] = change_issue_status
        if not allowed_status_transitions == "":
            vals["allowed_status_transitions"] = allowed_status_transitions
        return self._query(vals)

    def update_view(self, project, name, new_name="", query="", tags="", is_public=""):
        vals = {"action" : "update_view",
                "user" : self.user,
                "project" : project,
                "name" : name}
        if not new_name == "":
            vals["new_name"] = new_name
        if not query == "":
            vals["query"] = query
        if not tags == "":
            vals["tags"] = tags
        if is_public == "true" or is_public == "false":
            vals["is_public"] = is_public
        return self._query(vals)

    def users(self, search="", limit=""):
        vals = {"action" : "users",
                "user" : self.user}
        if not search == "":
            vals["search"] = search
        if not limit == "":
            vals["limit"] = limit
        return self._query(vals)

    def version(self, project):
        vals = {"action" : "version",
                "user" : self.user}
        return self._query(vals)

    def views(self, project):
        vals = {"action" : "views",
                "user" : self.user,
                "project" : project}
        return self._query(vals)
