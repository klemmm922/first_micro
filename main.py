from flask import Flask

app = Flask(__name__)

@app.route('/',methods=["GET"])
def hello_world():
 prefix_google = """
 <!-- Google tag (gtag.js) -->
<script async 
src="https://www.googletagmanager.com/gtag/js?id=G-XLPQT1T2SC"></script>
<script>
 window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
 gtag('config', 'G-XLPQT1T2SC');
</script>
 """
 return prefix_google + "Hello World"