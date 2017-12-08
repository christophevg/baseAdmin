var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  data: {
    message: "Dashboard message from Vue",
    drawer: null,
    items: [
      { icon: 'home',    text: 'Home',      path: "/"          },
      { icon: 'history', text: 'Dashboard', path: "/dashboard" },
    ]
  },
  props: {
    source: String
  }
});
