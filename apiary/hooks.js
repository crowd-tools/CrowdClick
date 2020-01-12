const hooks = require('hooks');

hooks.before('Task Collection > Create a new task', (transaction) => {
  transaction.request.headers.Authorization = 'Basic YWRtaW46YWRtaW4=';
});

hooks.before('Answer Collection > Create answer for task', (transaction) => {
  transaction.request.headers.Authorization = 'Basic YWRtaW46YWRtaW4=';
});

