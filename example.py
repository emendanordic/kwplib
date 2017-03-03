from kwplib import KwApiCon

t = KwApiCon(url="http://xubuntu:8080", user="emenda")

vals = {"action" : "builds",
        "project" : "git" }

# perform action "builds" on project git, on Klocwork server at xubuntu:8080
query_response = t.execute_query(vals)
# if response is None, then there was an error
if query_response.response == None:
    print "Error: " + query_response.error_msg
else:
    for i in query_response.response:
        print i

# example of using regular expression "git" to retrieve list of projects
# that match this regular expression
print t.get_project_list("git")
