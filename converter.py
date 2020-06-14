PREFIX = "#"


def get_config(d, ret=None, config=None, comment=None):

    if config is None:
      config = []
    if ret is None:
      ret = []

    for k, v in d.items():
      if v:
        if k == "_bundle":
          comment = str(v)
        elif k[:2] == "__":
          config.append({"type": "entryconfig", "path": list(ret), "entry": k.replace("__", ""), "values": v})
        elif type(v) == str and k[0] != "_":
          config.append({"type": "setter", "path": list(ret), "key": k.replace("_", "-"), "value": v})
        else:
          ret.append(k)

          if type(v) == dict:
            get_config(v, ret, config, comment)
          if type(v) == list:
            config.append({"type": "entrys", "path": list(ret), "entrys": v, "comment": comment})
          
          ret.pop()

    return config


def get_filtred_macros(value, values):
  if "@" in value:
    if "/" in value:
      c = 1
      subvalue = ""
      for v in value.split("/"):
        if c > 1:
          subvalue += "/"
        subvalue += values[v[1:]]
        c += 1
      return subvalue
    else:
      return values[value[1:]]
  else:
    return value


def get_commands_entrys(c, values):
  olders = []
  newers = []
  purges = []

  for e in c["entrys"]:

    path = " ".join(c["path"]).replace("__", "-")
    id_key = e["_identifier"]
    id_value = e[id_key]
    id_old = "#OLD#"

    # OLDER
    set_string = path + ' set {key}={id_old}{value} [find {key}={value}]'.format(key=id_key, value=id_value, id_old=id_old)
    if not set_string in olders:
      olders.append(set_string)

    # NEWER
    add_string = path + " add "
    for k in e:
      if k[0] != "_":
        value = get_filtred_macros(e[k], values)
        add_string += '{0}={1} '.format(k.replace("_", "-"), value)   
    newers.append(add_string)

    # PURGE
    purge_string = path + ' remove [find {id_key}~{id_old}]'.format(id_key=id_key, id_old=id_old)
    if not purge_string in purges:
      purges.append(purge_string)

  return {'olders': olders, 'newers': newers, 'purges': purges}


def get_commands_setter(c, values):
  value = get_filtred_macros(c["value"], values)
  return " ".join(c["path"]) + " set {0}={1}".format(c["key"], c["value"])


def get_commands_entryconfig(c, values):
  string = " ".join(c["path"]) + " set " + c["entry"]
  for k in c["values"]:
    value =  get_filtred_macros(c["values"][k], values)
    
    string += " {0}={1}".format(k.replace("_", "-"), c["values"][k])
  return string


def get_commands(config, values):
  result = []
  olders = []
  newers = []
  purges = []
  entryconfigs = []

  for c in config:

    if c["type"] == "entrys":
      r = get_commands_entrys(c, values)
      for i in (r["olders"]):
        olders.append(i)

      for i in (r["newers"]):
        newers.append(i)

      for i in (r["purges"]):
        purges.append(i)

    elif c["type"] == "setter":
      result.append(get_commands_setter(c, values))
    
    elif c["type"] == "entryconfig":
      entryconfigs.append(get_commands_entryconfig(c, values))

  result = result + olders + newers + purges + entryconfigs
  return result


def upload(commands, host, username, password, port=21):
  text = "\n".join(commands)
  send = io.BytesIO(bytes(text, 'utf-8'))

  session = ftplib.FTP(host, username, password, port)
  session.storbinary('STOR config.auto.rsc', send)
  session.quit()


def convert(collection, values):
  data = collection.find({'_bundle': values["bundle"]})[0]
  config = get_config(data)
  commands = get_commands(config, values)
  return commands
