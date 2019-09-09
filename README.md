# News app
Live demo: [http://hknewsapp.tk/](http://hknewsapp.tk/ "http://hknewsapp.tk/")

## Local build
`docker-compose up --build -d`

## API
http://hknewsapp.tk/posts
Takes 3 URL parameters:
- offset - positive integer value
- limit - positive integer below 150
- order - comma-separated list of ordering values (title, url, _id)

## Modules:
- **parser** - collects data from [news.ycombinator.com](https://news.ycombinator.com/ "news.ycombinator.com");
- **updater** - checks parsed data, saves it to database;
- **api** - displays collected data at JSON format, forces data update via parser module.
