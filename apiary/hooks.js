const hooks = require('hooks');

hooks.before('Task Collection  > Create a new task', (transaction) => {
  transaction.request.headers.Authorization = 'Basic: YWRtaW46YWRtaW4K';
});

hooks.before('Task Collection  > List All Tasks', (transaction) => {
  transaction.request.headers.Authorization = 'Basic: YWRtaW46YWRtaW4K';
});

