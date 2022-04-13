import json
import requests
import configparser


class AHT():

    def __init__(self, ahip):
        self.AHbaseURL= ahip

    def unregisterService(self):

        srvdef = aht.findService('addfacetofacemaskdb')

        if srvdef is not None:
            id=srvdef.get('id',None)
            if id is not None:

                url = self.AHbaseURL + '/serviceregistry/mgmt/' + str(id)
                myrequest = requests.delete(url)
                myresponse = myrequest.status_code
                if myresponse==200:
                    return True
                else:
                    print(myresponse)
                    return False



    def registerService(self, servername):

        url = self.AHbaseURL + '/serviceregistry/mgmt'

        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        dataPOST={"endOfValidity": "2022-03-31 16:29:53",
                  "interfaces": ["HTTP-SECURE-JSON"],
                  "metadata": {
                    "Company": "UniMoRe",
                    "Author": "Roberto Vezzani",
                    "Description": "Add a face to the db for the annotation of mask/notMask"
                  },
                  "providerSystem": {
                    "address": servername,
                    "authenticationInfo": "fweWf24exc.#234",
                    "port": 443,
                    "systemName": "AHT-MoRe-Masks"
                  },
                  "secure": "NOT_SECURE",
                  "serviceDefinition": "AddFaceToFaceMaskDB",
                  "serviceUri": "uploadimagewithkey",
                  "version": 0
                }


        myrequest = requests.post(url, json=dataPOST,  headers=headers)
        myresponse = myrequest.text

        print(myresponse)

    def getListOfServices(self):
        listService=[]
        url = self.AHbaseURL + '/serviceregistry/mgmt?direction=ASC&sort_field=id'
        headers = dict()
        headers['Accept']='*/*'

        myrequest = requests.get (url,  headers=headers)
        dataget = myrequest.text
        fileOut= open('services.txt','w')
        fileOut.write(dataget )
        fileOut.close()
        print(dataget)

    def findService(self, name):
        listService = []
        url = self.AHbaseURL + '/serviceregistry/mgmt?direction=ASC&sort_field=id'
        headers = dict()
        headers['Accept'] = '*/*'

        myrequest = requests.get(url, headers=headers)
        dataget = myrequest.text
        jsonservices = json.loads(dataget)
        for serv in jsonservices['data']:
            srvdef = serv.get('serviceDefinition',dict())
            if srvdef.get('serviceDefinition','') == name:
                # servizio trovato
                return serv
        return None

def geturlFromSrcdef(srvdef):
    myurl='nd'
    if srvdef is None:
        return ''
    provider = srvdef.get('provider',None)
    if provider['port']==443:
        myurl = 'https://'
    else:
        myurl = 'http://'
    myurl += provider['address']
    myurl +='/'
    myurl += srvdef.get('serviceUri')
    #if (srvdef.get['servi'])

    return myurl

if __name__=='__main__':
    Config = configparser.ConfigParser()
    conf = Config.read("gateway.ini")


    aht = AHT(Config.get('General','BASEURL'))
    #print (aht.getListOfServices())
    srvdef = aht.findService('addfacetofacemaskdb')
    print('url service before reg: ' + geturlFromSrcdef(srvdef))

    aht.unregisterService()

    aht.registerService(Config.get('FaceMask','SERVER'))

    srvdef = aht.findService('addfacetofacemaskdb')
    print('url service after reg: ' + geturlFromSrcdef(srvdef))