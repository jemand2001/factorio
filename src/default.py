from parse_exchange import ExchangeStringParser


exchange_string = '''>>>eNpjZEAAewaGA/YcLMn5iTmrV62yY2BwcACKOHAl5xcUpBbp5hel
IgtzJheVpqTq5meiKk7NS82t1E1KLE5lYGiwh2GOzKL8PHQTWItL8vN
QRUqKUlOLkTVylxYl5mWW5qLrZWDM39y/rqFFjgGE/9czKPz/D8JA1g
OgV0CYgbEBbAojUAwGWJNzMtPSGBgUHIHYCSTNyMhYLbLO/WHVFHtGi
Bo9ByjjA1TkQBJMxBPG8HPAKaUCY5ggmWMMBp+RGBBLS4BWQFVxOCAY
EMkWkCQjY+/brQu+Hztgx/hn5cdLvkkJ9oyGriLvPhitswNKs4P8yQQ
nZs0EgZ0wrzDAzHxgD5W6ac949gwIvLFnZAXpEAERDhZA4oA3MwOjAB
+QtaAHSCjIMMCcZgczRsSBMQ0MvsF88hjGuGyP7g9gQNiADJcDESdAB
NhCuMsYIUyHfgdGB3mYrCRCCVC/EQOyG1IQPjwJs/Ywkv1oDsGMCGR/
oImoOGCJBi6QhSlw4gUz3DXA8LzADuM5zHdgZAYxQKq+AMUgPJAMzCg
ILeDAjJTdgMni+acicwCQlaq1<<<'''


parser = ExchangeStringParser(exchange_string)

if __name__ == '__main__':
    for i in parser:
        print(*i, sep=': ')
    rest = len(parser) - parser.index
    print(f'there are {rest} bytes left in the decompressed data')
