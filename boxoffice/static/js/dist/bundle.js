(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var Router = require("./router").Router;

$(function () {
  var appRouter = new Router();
  Backbone.history.start({ pushState: true, root: "/admin/" });
  window.eventBus = _.clone(Backbone.Events);
  window.eventBus.on("navigate", function (msg) {
    appRouter.navigate(msg, { trigger: true });
  });
});

},{"./router":8}],2:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var IndexModel = Backbone.Model.extend({
  url: function url() {
    return "/admin/dashboard";
  }
});
exports.IndexModel = IndexModel;

},{}],3:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var OrgModel = Backbone.Model.extend({
  url: function url(name) {
    console.log(this.get("name"));
    return "/admin/o/" + this.get("name");
  }
});
exports.OrgModel = OrgModel;

},{}],4:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var IndexTemplate = "\n  {{#orgs}}\n    <a href=\"javascript:void(0)\" on-click=\"navigate\">{{title}}</a>\n  {{/}}\n";
exports.IndexTemplate = IndexTemplate;

},{}],5:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var orgTemplate = "\n  <p>Hello, {{name}}!</p>\n  {{#item_collections}}\n    <h3>{{name}}</h3>\n  {{/}}\n";
exports.orgTemplate = orgTemplate;

},{}],6:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var IndexModel = require("../models/index.js").IndexModel;

var IndexTemplate = require("../templates/index.html.js").IndexTemplate;

var IndexView = {
  render: function render() {
    console.log(!this.ractive);
    if (!this.indexModel) {
      this.indexModel = new IndexModel();
    }
    this.indexModel.fetch().then(function (data) {
      if (!this.ractive) {
        console.log("ractive");
        this.ractive = new Ractive({
          el: "#main-content-area",
          template: IndexTemplate,
          data: {
            orgs: data.orgs
          }
        });
        this.ractive.on("navigate", function (event, method) {
          // console.log(event.context.url);
          eventBus.trigger("navigate", event.context.url);
        });
      } else {
        this.ractive.render();
      }
    });
  }
};
exports.IndexView = IndexView;

},{"../models/index.js":2,"../templates/index.html.js":4}],7:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var OrgModel = require("../models/org.js").OrgModel;

var orgTemplate = require("../templates/org.html.js").orgTemplate;

var OrgView = {
  render: function render(org) {
    console.log(orgTemplate);
    if (!this.orgModel) {
      this.orgModel = new OrgModel({
        name: org.name
      });
    }
    this.orgModel.fetch().then(function (data) {
      if (!this.ractive) {
        this.ractive = new Ractive({
          el: "#main-content-area",
          // template: '#org-content-template',
          template: orgTemplate,
          data: {
            name: data.name,
            item_collections: data.item_collections
          }
        });
      } else {
        this.ractive.render();
      }
    });
  }
};
exports.OrgView = OrgView;

},{"../models/org.js":3,"../templates/org.html.js":5}],8:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var IndexView = require("./index.js").IndexView;

var _orgJs = require("./org.js");

var OrgView = _orgJs.OrgView;
var ItemCollectionView = _orgJs.ItemCollectionView;
var Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:ic": "item_collection"
  },
  index: function index() {
    IndexView.render();
  },
  org: (function (_org) {
    var _orgWrapper = function org(_x) {
      return _org.apply(this, arguments);
    };

    _orgWrapper.toString = function () {
      return _org.toString();
    };

    return _orgWrapper;
  })(function (org) {
    OrgView.render({ name: org });
  }),
  item_collection: function item_collection(ic) {
    ItemCollectionView.render({ name: ic });
  }
});
exports.Router = Router;

},{"./index.js":6,"./org.js":7}]},{},[1])
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL21haW4uanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL21vZGVscy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3RlbXBsYXRlcy9vcmcuaHRtbC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3MvaW5kZXguanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3Mvcm91dGVyLmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBOzs7SUNDUSxNQUFNLFdBQU8sVUFBVSxFQUF2QixNQUFNOztBQUdkLENBQUMsQ0FBQyxZQUFVO0FBQ1YsTUFBSSxTQUFTLEdBQUcsSUFBSSxNQUFNLEVBQUUsQ0FBQztBQUM3QixVQUFRLENBQUMsT0FBTyxDQUFDLEtBQUssQ0FBQyxFQUFDLFNBQVMsRUFBRSxJQUFJLEVBQUUsSUFBSSxFQUFFLFNBQVMsRUFBQyxDQUFDLENBQUM7QUFDM0QsUUFBTSxDQUFDLFFBQVEsR0FB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QUksRUFBRSxFQUFFLEVBQUMsQ0FBQyxDQUFDO0dBQ3ZDO0NBQ0YsQ0FBQyxDQUFDO1FBZlUsTUFBTSxHQUFOLE1BQU0iLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiXG5pbXBvcnQge1JvdXRlcn0gZnJvbSAnLi9yb3V0ZXInO1xuXG5cbiQoZnVuY3Rpb24oKXtcbiAgbGV0IGFwcFJvdXRlciA9IG5ldyBSb3V0ZXIoKTtcbiAgQmFja2JvbmUuaGlzdG9yeS5zdGFydCh7cHVzaFN0YXRlOiB0cnVlLCByb290OiBcIi9hZG1pbi9cIn0pO1xuICB3aW5kb3cuZXZlbnRCdXMgPSBfLmNsb25lKEJhY2tib25lLkV2ZW50cyk7XG4gIHdpbmRvdy5ldmVudEJ1cy5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihtc2cpe1xuICAgIGFwcFJvdXRlci5uYXZpZ2F0ZShtc2csIHt0cmlnZ2VyOiB0cnVlfSk7XG4gIH0pXG59KTtcblxuIiwiXG5leHBvcnQgY29uc3QgSW5kZXhNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKCl7XG4gICAgcmV0dXJuICcvYWRtaW4vZGFzaGJvYXJkJztcbiAgfVxufSk7XG4iLCJcbmV4cG9ydCBjb25zdCBPcmdNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKG5hbWUpe1xuICAgIGNvbnNvbGUubG9nKHRoaXMuZ2V0KCduYW1lJykpO1xuICAgIHJldHVybiAnL2FkbWluL28vJyArIHRoaXMuZ2V0KCduYW1lJyk7XG4gIH1cbn0pO1xuIiwiZXhwb3J0IGNvbnN0IEluZGV4VGVtcGxhdGUgPSBgXG4gIHt7I29yZ3N9fVxuICAgIDxhIGhyZWY9XCJqYXZhc2NyaXB0OnZvaWQoMClcIiBvbi1jbGljaz1cIm5hdmlnYXRlXCI+e3t0aXRsZX19PC9hPlxuICB7ey99fVxuYFxuIiwiZXhwb3J0IGNvbnN0IG9yZ1RlbXBsYXRlID0gYFxuICA8cD5IZWxsbywge3tuYW1lfX0hPC9wPlxuICB7eyNpdGVtX2NvbGxlY3Rpb25zfX1cbiAgICA8aDM+e3tuYW1lfX08L2gzPlxuICB7ey99fVxuYFxuIiwiXG5pbXBvcnQge0luZGV4TW9kZWx9IGZyb20gJy4uL21vZGVscy9pbmRleC5qcyc7XG5pbXBvcnQge0luZGV4VGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pbmRleC5odG1sLmpzJztcblxuZXhwb3J0IGNvbnN0IEluZGV4VmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbigpIHtcbiAgICBjb25zb2xlLmxvZyghdGhpcy5yYWN0aXZlKTtcbiAgICBpZiAoIXRoaXMuaW5kZXhNb2RlbCkge1xuICAgICAgdGhpcy5pbmRleE1vZGVsID0gbmV3IEluZGV4TW9kZWwoKTtcbiAgICB9XG4gICAgdGhpcy5pbmRleE1vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIGlmICghdGhpcy5yYWN0aXZlKSB7XG4gICAgICAgIGNvbnNvbGUubG9nKFwicmFjdGl2ZVwiKVxuICAgICAgICB0aGlzLnJhY3RpdmUgPSBuZXcgUmFjdGl2ZSh7XG4gICAgICAgICAgZWw6ICcjbWFpbi1jb250ZW50LWFyZWEnLFxuICAgICAgICAgIHRlbXBsYXRlOiBJbmRleFRlbXBsYXRlLFxuICAgICAgICAgIGRhdGE6IHtcbiAgICAgICAgICAgIG9yZ3M6IGRhdGEub3Jnc1xuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICAgIHRoaXMucmFjdGl2ZS5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihldmVudCwgbWV0aG9kKXtcbiAgICAgICAgICAvLyBjb25zb2xlLmxvZyhldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgIH0pO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlLnJlbmRlcigpO1xuICAgICAgfVxuICAgIH0pXG4gIH1cbn1cbiIsIlxuaW1wb3J0IHtPcmdNb2RlbH0gZnJvbSAnLi4vbW9kZWxzL29yZy5qcyc7XG5pbXBvcnQge29yZ1RlbXBsYXRlfSBmcm9tICcuLi90ZW1wbGF0ZXMvb3JnLmh0bWwuanMnO1xuXG5leHBvcnQgY29uc3QgT3JnVmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbihvcmcpIHtcbiAgICBjb25zb2xlLmxvZyhvcmdUZW1wbGF0ZSk7XG4gICAgaWYgKCF0aGlzLm9yZ01vZGVsKSB7XG4gICAgICB0aGlzLm9yZ01vZGVsID0gbmV3IE9yZ01vZGVsKHtcbiAgICAgICAgbmFtZTogb3JnLm5hbWVcbiAgICAgIH0pO1xuICAgIH1cbiAgICB0aGlzLm9yZ01vZGVsLmZldGNoKCkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgIGlmICghdGhpcy5yYWN0aXZlKSB7XG4gICAgICAgIHRoaXMucmFjdGl2ZSA9IG5ldyBSYWN0aXZlKHtcbiAgICAgICAgICBlbDogJyNtYWluLWNvbnRlbnQtYXJlYScsXG4gICAgICAgICAgLy8gdGVtcGxhdGU6ICcjb3JnLWNvbnRlbnQtdGVtcGxhdGUnLFxuICAgICAgICAgIHRlbXBsYXRlOiBvcmdUZW1wbGF0ZSxcbiAgICAgICAgICBkYXRhOiB7XG4gICAgICAgICAgICBuYW1lOiBkYXRhLm5hbWUsXG4gICAgICAgICAgICBpdGVtX2NvbGxlY3Rpb25zOiBkYXRhLml0ZW1fY29sbGVjdGlvbnNcbiAgICAgICAgICB9XG4gICAgICAgIH0pO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlLnJlbmRlcigpO1xuICAgICAgfVxuICAgIH0pO1xuXG4gIH1cbn1cbiIsIlxuaW1wb3J0IHtJbmRleFZpZXd9IGZyb20gJy4vaW5kZXguanMnO1xuaW1wb3J0IHtPcmdWaWV3fSBmcm9tICcuL29yZy5qcyc7XG5pbXBvcnQge0l0ZW1Db2xsZWN0aW9uVmlld30gZnJvbSAnLi9vcmcuanMnO1xuXG5leHBvcnQgY29uc3QgUm91dGVyID0gQmFja2JvbmUuUm91dGVyLmV4dGVuZCh7XG4gIHJvdXRlczoge1xuICAgIFwiXCI6IFwiaW5kZXhcIixcbiAgICBcIm8vOm9yZ1wiOiBcIm9yZ1wiLFxuICAgIFwiaWMvOmljXCI6IFwiaXRlbV9jb2xsZWN0aW9uXCJcbiAgfSxcbiAgaW5kZXg6IGZ1bmN0aW9uKCkge1xuICAgIEluZGV4Vmlldy5yZW5kZXIoKTtcbiAgfSxcbiAgb3JnOiBmdW5jdGlvbihvcmcpe1xuICAgIE9yZ1ZpZXcucmVuZGVyKHtuYW1lOiBvcmd9KTtcbiAgfSxcbiAgaXRlbV9jb2xsZWN0aW9uOiBmdW5jdGlvbihpYyl7XG4gICAgSXRlbUNvbGxlY3Rpb25WaWV3LnJlbmRlcih7bmFtZTogaWN9KTtcbiAgfVxufSk7XG4iXX0=
