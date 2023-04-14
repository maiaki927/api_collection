import json
from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import os
import openai
import requests
import re
import ast

app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

openaikey=os.environ.get("openaiSECRET")
reurlkey=os.environ.get("reurlSECRET")
ipfskey=os.environ.get("ipfs")
openai.api_key =openaikey

from bs4 import BeautifulSoup




class Getreurl(Resource):
   def post(self):
      data2 = request.get_json() 
      url = 'https://api.reurl.cc/shorten'
      myobj = {"url" : data2["url"]}
      headers = {'Content-Type': 'application/json',"reurl-api-key": reurlkey}
      print(url)
      print(myobj)
      print(headers)
      x = requests.post(url, json=myobj,headers=headers)
      x=x.json()

      return x['short_url']
   def getUrl(self,ourl):
      url = 'https://api.reurl.cc/shorten'
      myobj = {"url" : ourl}
      headers = {'Content-Type': 'application/json',"reurl-api-key": reurlkey}
      print(url)
      print(myobj)
      print(headers)
      x = requests.post(url, json=myobj,headers=headers)
      x=x.json()
      print(x)
      return x['short_url']


class Generateimg(Resource):    
    
    def __init__(self):
        self.url=Getreurl()
     
    
    def post(self):       
          
        data = request.get_json() 
        
        try: 
            if data['description']!='':
                response = openai.Image.create(
                prompt=data['description'],
                n=1,
                size="512x512"
                )
                image_url = response['data'][0]['url']
                print(image_url)
        except Exception as e:
            print(str(e))
            return jsonify({'Message': 'Error:'+str(e)}) 
                  
        return jsonify({'Message': "Success","url":image_url})

      
class GetData(Resource):             
    def get(self):
        address=request.args.get('address')

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'content-type': 'application/javascript'
      }
        redata=[]
        url = "https://ethtx.info/goerli/"+address+"/"
        
        response = requests.get(url, headers=headers, timeout=50)
        print(response)
        # 檢查是否成功獲取HTML
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            target_elems = soup.find_all(text=re.compile(r'\[\[(.*?)\]\]'))
    
            for target_elem in target_elems:
                  match = re.search(r'\[\[.*\]\]', target_elem)
                  if match:
                      result = match.group()
                      
                      redata.append(ast.literal_eval(result))
            print(redata)
            
        else:
            print("Failed to retrieve HTML from " + url)
        return jsonify({'message': redata})
       
    
      

      
class Getjsonurl(Resource):    
             
    def get(self):
        return jsonify({'message': "This api is only post"})
     
    
    def post(self):       
        data = request.get_json()       

        try:
            print()
            headers = {'Authorization': 'Basic <base64(2LbbuhNdjM2Vg8vWzYzBIDPVhJC:'+ipfskey+')>'}

            endpoint = "https://ipfs.infura.io:5001"

            ### CREATE AN ARRAY OF TEST FILES ###
            
            files = {
            'file': str(data)
            }
            
            print(files)
            projectId='2MnlfrdEQ5BqDbZ7UsZ9XNwB5c0'
            
            ### ADD FILE TO IPFS AND SAVE THE HASH ###
            response1 = requests.post(endpoint + '/api/v0/add', files=files, auth=(projectId, ipfskey))
            print(response1)   
            
            hash = response1.text.split(",")[1].split(":")[1].replace('"','')
            print(hash)

            ### READ FILE WITH HASH ###
            params = {
                'arg': hash
            }
            response2 = requests.post(endpoint + '/api/v0/cat', params=params, auth=(projectId, ipfskey))
            print(response2)
            print('here',response2.text)

      
        except Exception as e:
            return jsonify({'Error': str(e)})     
              
        return jsonify({'Message': "Success",'url':'https://ipfs.io/ipfs/'+hash}) 

      

      
api.add_resource(Generateimg, '/api/generateimg')
api.add_resource(Getreurl, '/api/getreurl')
api.add_resource(Getjsonurl, '/api/getjsonurl')
api.add_resource(GetData, '/api/getdata')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)