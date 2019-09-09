db.createCollection('posts');
db.createCollection('updates');
db.posts.createIndex({url: 1, title: 1});
