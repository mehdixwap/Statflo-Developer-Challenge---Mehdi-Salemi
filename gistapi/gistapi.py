# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request, render_template

import requests
import json
import urllib2
import re

#from flask.ext.mysql import MySQL

# *The* app object
app = Flask(__name__)

"""
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Medmed77'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    
    gists_url = 'https://api.github.com/users/{username}/gists?per_page=3000'.format(
            username=username)
    # BONUS: What failures could happen?
    
    # Possible failure could be if the user does not exist or another error occurs that 
    # will not return a list. The status code will be 200 if successfull.
    response = requests.get(gists_url)
    
    if (response.status_code != 200):
        return -1
    
    # BONUS: Paging? How does this work for users with tons of gists?
    # Looking through the GitHub api, we can add the '?per_page=3000' in the api call to
    # allow the the maximum amount to be returned instead of the deault of 30.
    
    return json.loads(response.text)

def pattern_in(pattern, URL):
    content = urllib2.urlopen(URL).read()
    matches = re.findall(pattern, content)
    
    if (len(matches) > 0):
        return True
    else:
        return False
    


@app.route("/search_API_v1", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    
    """
        For this section I made small revision to the way that was outlined.
        I use a slightly different way to test for a pattern match, I went through the GitHub API
        and could find a way to see patterns in Gist code, only for Repo's. So I decided to to the 
        raw text url of the file that I found when inspecting the JSON response from the initial gist list
        from the user. Then I look through the text for the pattern. Might not be optimal for super large 
        files, but give then time I have to complete I decided to choose thise option.
    
        Also, I added a very simple home page so the user can choose the pattern and the username to search for.
    """
    
    result = {}
    
    username = request.form["username"]
    
    gists = gists_for_user(username)
    
    # BONUS: Handle invalid users
    if (gists == -1):
        return "'" + username + "'" + " could not be on GitHub."
    else:
        result["username"] = username
        result['pattern'] = request.form["pattern"]
    
    result["matches"] = []
    
    for gist in gists:
        for key, value in gist["files"].iteritems():
            if (pattern_in(request.form["pattern"], value["raw_url"])):
                result["matches"].append(str(key))
    
    """
    # BONUS: What about huge gists?
    # BONUS: Can we cache results in a datastore/db?
    ### Attempt to add SQL for large GIST
    cur = mysql.connection.cursor()
    
    cur.execute("CREATE DATABASE IF NOT EXISTS gists;")
    cur.execute("USE gists;")
    cur.execute(createGistTable(result["username"]))
    
    for gist in gists:
        for key, value in gist["files"].iteritems():
            insertToGistTable(result["username"], value["raw_url"], cur)

    Did not keep this section in as I wasn't sure if this was optimal or not. My plan was to:
    1. Create table and import all GIST into it if GIST list is large (ie greater than X)
    2. Search through that GIST list for pattern match
    2.1. remove item that doesn't match
    3. return the list of items that matched and do that same I do regular sized lists.  
    """
    
    return render_template("search_API_V1.html", results=result)


### Functions for my idea for adding database which isnt implemnted
def createGistTable(username):
    table = "CREATE TABLE " + username +"GistList (filename VARCHAR(20), url VARCHAR(50), PRIMARY KEY(url));"
    return table

def insertToGistTable(username, url, cur):
    
    insert = "INSERT INTO " +username+ +"GistList VALUES '" +username+ "', '" +url+ "');"
    
    curr.execute()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
