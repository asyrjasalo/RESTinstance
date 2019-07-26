function(request, state, logger, callback) {

  const proxy = require(`${process.cwd()}/testapi/responders/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    const state_was = state.instances[response.token].responses;

    state.instances[response.token].responses = {};

    response = {
      statusCode: 204,
      body: JSON.stringify(state_was)
    }

    callback(response);
  });
}
