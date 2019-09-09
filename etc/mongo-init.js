db.createCollection('posts');
db.posts.createIndex({url: 1, title: 1});
