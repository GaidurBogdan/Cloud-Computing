#!C:\Users\bgaid\AppData\Local\Programs\Python\Python37-32\python.exe

import cgi, cgitb, urllib, json
from urllib.request import Request, urlopen
from unidecode import unidecode

form = cgi.FieldStorage() 

country = form.getvalue('country')

file = open("../logs/logfile.txt","w+")

# Returns a random number between 1 and 10 as an integer.
# https://www.random.org/clients/http/#integers
def callRandomAPI():
    req = Request("https://www.random.org/integers/?num=1&min=1&max=10&col=1&base=10&format=plain&rnd=new")
    req.add_header('accept', 'application/hal+json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')

    contents = urlopen(req)

    file.write("\n\nRandom API Request:\n\n")
    file.write(str(req.headers))
    file.write('\n')
    file.write(str(req.data))

    file.write("\n\nRandom API Response:\n\n")
    file.write(str(contents.headers))
    file.write('\n')

    randomNumber = str(contents.read()).replace('\\n',' ').replace('b','')[1:-1].split(' ')
    randomNumber = int(randomNumber[0])

    file.write(str(randomNumber))
    
    return randomNumber

# Returns the official language of the called country as a lowercase abbreviation
# comprised of 2 letters. ( ro, en, de ...)
# https://restcountries.eu/#api-endpoints-name
def callCountryAPI():
    req = Request("https://restcountries.eu/rest/v2/name/" + str(country))
    req.add_header('accept', 'application/hal+json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')

    response = urlopen(req)

    file.write("\n\nCountry API Request:\n\n")
    file.write(str(req.headers))
    file.write('\n')
    file.write(str(req.data))

    file.write("\n\nCountry API Response:\n\n")
    file.write(str(response.headers))
    file.write('\n')
    # file.write(json.load(response))

    response = json.load(response)
    return str(response[0]['languages'][0]['iso639_1'])

# Returns a number of songs equal to the random number generated in the callRandomAPI,
# sung in the official language of the country introduced in the form. The returned list 
# is comprised of pairs like this: song - artist.
# https://developer.musixmatch.com/documentation/api-reference/track-search
def callMusicAPI():
    apikeyFile = open("../configs/cheieMusicxMatch.txt", "r")
    apikey = apikeyFile.read()
    apikeyFile.close()
    req = Request("http://api.musixmatch.com/ws/1.1/track.search?f_lyrics_language=" + str(callCountryAPI()) + "&page_size=" + str(callRandomAPI()) + "&page=1&s_track_rating=desc&apikey=" + str(apikey))
    req.add_header('accept', 'application/hal+json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')

    response = urlopen(req)

    file.write("\n\nMusic API Request:\n\n")
    file.write(str(req.headers))
    file.write('\n')
    file.write(str(req.data))

    file.write("\n\nMusic API Response:\n\n")
    file.write(str(response.headers))
    file.write('\n')
    # json.dump(json.load(response), file)

    response = json.load(response)
    songs = []
    for song in response["message"]["body"]["track_list"]:
        songs.append((song["track"]["track_name"], song["track"]["artist_name"]))
    return songs

tracklist = callMusicAPI()
response = '<html><body>'

for track in tracklist:
    response += '<p>' + str(unidecode(track[0])) + ' - ' + str(unidecode(track[1])) + '</p></br></br>'

response += '</body></html>'

print ("Content-type:text/html\r\n\r\n")
print (response)
