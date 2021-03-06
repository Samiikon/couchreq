import sys
import os
import json
import requests
import pkg_resources


class Couchreq:
    def __init__(self):
        """Create new Couchreq instance."""
        resource_pkg = __name__
        resource_path = 'config.json'
        configpath = pkg_resources.resource_filename(resource_pkg, resource_path)
        
        with open(configpath) as config:
            data = json.load(config)
        
        # Default: http://127.0.0.1:5984/
        self.baseurl = 'http://' + data['urls']['base'] + ':' + \
                        data['urls']['port'] + '/'

        # Url for admin requests(create & delete db)
        # Default: http://user:password@127.0.0.1:5984/
        self.adminurl = 'http://' + data['admin']['username'] + ':' + \
                        data['admin']['password'] + '@' + \
                        data['urls']['base'] + ':' + data['urls']['port'] + '/'


    def create_db(self, dbname):
        """Create new db with given name, if db with that name doesn't exist.

        Args:
            dbname(str): Name for the new database.

        At the time of writing this code, CouchDB has a small bug when using
        admin rights. For example, when new db is created, CDB returns http 
        status code 500 instead of 200. This just doesn't mean that something 
        went wrong, and is the main reason why I decided to check if just 
        created db actually exists. Without the bug, there would be also a 
        check for http code too.

        Issue of the bug: https://issues.apache.org/jira/browse/COUCHDB-2946
        """
        if not dbname:
            return False


        if self.db_exists(dbname):
            return 'Database with name ' + dbname + ' already exists!'
        
        r = requests.put(self.adminurl + dbname)

        if self.db_exists(dbname):
            return 'Database ' + dbname + ' created!'
        
        return 'Something may have gone wrong!'


    def delete_db(self, dbname):
        """Checks if given db exists and then simply deletes it, no questions asked.

        Args:
            dbname(str): Name of the database to delete.

        ATTENTION! Be sure what database you are deleting as this function just 
        deletes db with no questions asked.
        """

        if not self.db_exists(dbname):
            return 'Db with name ' + dbname + ' was not found!'
        
        r = requests.delete(self.adminurl + dbname)
        
        if not self.db_exists(dbname):
            return 'Database ' + dbname + ' was deleted!' 


    def create_doc(self, dbname, docdata, docid = None):
        """Create new document to the given database.

        If docid is not given, function uses id generated by CouchDB.

        Args:
            dbname(str): Name of the database where new document is created.
            docdata(dict): Data for the new document
        """

        if not docid:
            docid = self.get_uuid()

        if not self.doc_exists(dbname, docid):
            r = requests.put(self.baseurl + dbname + '/' + str(docid), json=docdata)
            
            if r.status_code in [201, 202]:
                return 'New document created to ' + dbname + ' database!'

        return 'Creating new document to ' + dbname + ' database failed!'


    def get_doc(self, dbname, docid):
        """Return document with given id from given database as a dict."""

        r = requests.get(self.baseurl + dbname + '/' + docid)
        return r.json()


    def delete_doc(self, dbname, docid):
        """Delete given document from given database.

        As is the nature of CouchDB, document is not fully deleted. Document with 
        very limited data is left behind, to enable the replication of this delete
        action for other possible nodes. This tombstone of a document doesn't show 
        in db requests.

        Args:
            dbname(str): Name of the database from where the document is deleted.
        """

        if self.doc_exists(dbname, docid):
            revision = self.get_revision(dbname, docid)

            r = requests.delete(self.baseurl + dbname + '/' + docid, params={'rev': revision})
            
            if not self.doc_exists(dbname, docid):
                return 'Deletion successful!'
            return 'Deletion failed, something went wrong!'
        return 'Deletion failed, document not found!'


    def all_dbs(self):
        """Return names of all databases in local CouchDB as a list."""

        r = requests.get(self.baseurl + '_all_dbs')
        return r.json()


    def db_exists(self, dbname):
        """Check if database with given dbname exists within local CouchDB."""

        r = requests.get(self.baseurl + dbname)
        
        if r.status_code == 200:
            dbs = self.all_dbs()

            if dbname in dbs:
                return True
            return False
        return False


    def doc_exists(self, dbname, docid):
        """Check if document with given id in specified database exists."""

        r = requests.get(self.baseurl + dbname + '/' + docid)

        if r.status_code == 200:
            return True
        
        return False


    def get_revision(self, dbname, docid):
        """Return revision for a document as a string."""

        docdata = self.get_doc(dbname, docid)    
        return docdata['_rev']


    def get_uuid(self):
        """Return new uuid generated by CouchDB."""

        r = requests.get(self.baseurl + '_uuids') 
        return r.json()['uuids'][0]
