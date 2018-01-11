function(request, state, logger, callback) {

  if (!request.body) return {};

  var params = JSON.parse(request.body);
  if (!params.id) {
    return {
      body: { "error": "No property 'id' given" }
    }
  }

  request.path = request.path + '/' + params.id;

  const proxy = require(`${process.cwd()}/apis/mocks/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode == 200 || response.statusCode == 201) {
      response = {
        statusCode: 404,
        body: { "error": "Already exists" }
      }
    }
    else {
      response = {
        statusCode: 201,
        body: request.body
      }
      state.responses[request.path] = response;
    }
    callback(response);
  });

}
