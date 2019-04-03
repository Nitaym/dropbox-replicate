import urllib.parse
import boto3

index_start = '''
<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>
<body>
'''

index_end = '''
</body>
</html>
'''


def bucket_to_website(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    folder = 'Tapes/'
    ls = bucket.objects.filter(Prefix=folder)
    keys = []
    for item in ls:
        if folder == item.key:
            continue

        key = item.key.replace(folder, '')
        url = 'https://s3.amazonaws.com/%s/%s' % (bucket_name, urllib.parse.quote(item.key))

        keys += [(key, url)]
        print('%s  %s' % (item.key, url))

    pages = index_start
    for key in keys:
        pages += '<a href=%s>%s</a><br><br>' % (key[1], key[0])
    pages += index_end

    with open('index.html', 'w', encoding='utf8') as f:
        f.write(pages)


if __name__ == "__main__":
    bucket_to_website('saba-tapes')
