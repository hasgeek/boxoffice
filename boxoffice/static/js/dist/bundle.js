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

},{"./router":11}],2:[function(require,module,exports){
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
var ItemCollectionModel = Backbone.Model.extend({
  url: function url(id) {
    return "/admin/ic/" + this.get("id");
  }
});
exports.ItemCollectionModel = ItemCollectionModel;

},{}],4:[function(require,module,exports){
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

},{}],5:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var IndexTemplate = "\n  {{#orgs}}\n    <a href=\"javascript:void(0)\" on-click=\"navigate\">{{title}}</a>\n  {{/}}\n";
exports.IndexTemplate = IndexTemplate;

},{}],6:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var ItemCollectionTemplate = "\n  {{#items}}\n    <h3>{{title}}</h3>\n  {{/}}\n";
exports.ItemCollectionTemplate = ItemCollectionTemplate;

},{}],7:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
var orgTemplate = "\n  <p>Hello, {{name}}!</p>\n  {{#item_collections}}\n    <h3>{{name}}</h3>\n  {{/}}\n";
exports.orgTemplate = orgTemplate;

},{}],8:[function(require,module,exports){
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

},{"../models/index.js":2,"../templates/index.html.js":5}],9:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var ItemCollectionModel = require("../models/item_collection.js").ItemCollectionModel;

var ItemCollectionTemplate = require("../templates/item_collection.html.js").ItemCollectionTemplate;

var ItemCollectionView = {
  render: function render(initData) {
    console.log(!this.ractive);
    if (!this.model) {
      this.model = new ItemCollectionModel({
        id: initData.id
      });
    }
    this.model.fetch().then(function (data) {
      if (!this.ractive) {
        this.ractive = new Ractive({
          el: "#main-content-area",
          template: ItemCollectionTemplate,
          data: {
            items: data.items
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
exports.ItemCollectionView = ItemCollectionView;

},{"../models/item_collection.js":3,"../templates/item_collection.html.js":6}],10:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var OrgModel = require("../models/org.js").OrgModel;

// import {renderview} from './renderview.js';

var orgTemplate = require("../templates/org.html.js").orgTemplate;

var OrgView = {
  render: function render(org) {
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

},{"../models/org.js":4,"../templates/org.html.js":7}],11:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var IndexView = require("./index.js").IndexView;

var OrgView = require("./org.js").OrgView;

var ItemCollectionView = require("./item_collection.js").ItemCollectionView;

var Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection"
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
  item_collection: function item_collection(icId) {
    ItemCollectionView.render({ id: icId });
  }
});
exports.Router = Router;

},{"./index.js":8,"./item_collection.js":9,"./org.js":10}]},{},[1])
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3ZpZXdzL21haW4uanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL21vZGVscy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvbW9kZWxzL29yZy5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL2luZGV4Lmh0bWwuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGljL2pzL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdGVtcGxhdGVzL29yZy5odG1sLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9pbmRleC5qcyIsIi9ob21lL3NocmV5YXMvZGV2L2hhc2dlZWsvYm94b2ZmaWNlL2JveG9mZmljZS9zdGF0aWMvanMvdmlld3MvaXRlbV9jb2xsZWN0aW9uLmpzIiwiL2hvbWUvc2hyZXlhcy9kZXYvaGFzZ2Vlay9ib3hvZmZpY2UvYm94b2ZmaWNlL3N0YXRpYy9qcy92aWV3cy9vcmcuanMiLCIvaG9tZS9zaHJleWFzL2Rldi9oYXNnZWVrL2JveG9mZmljZS9ib3hvZmZpY2Uvc3RhdGlj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RUFBQyxFQUFFLEVBQUUsSUFBSSxFQUFDLENBQUMsQ0FBQztHQUN2QztDQUNGLENBQUMsQ0FBQztBQWtCSCxPQUFPLENBakNNLE1BQU0sR0FBTixNQUFNLENBQUEiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiXG5pbXBvcnQge1JvdXRlcn0gZnJvbSAnLi9yb3V0ZXInO1xuXG5cbiQoZnVuY3Rpb24oKXtcbiAgbGV0IGFwcFJvdXRlciA9IG5ldyBSb3V0ZXIoKTtcbiAgQmFja2JvbmUuaGlzdG9yeS5zdGFydCh7cHVzaFN0YXRlOiB0cnVlLCByb290OiBcIi9hZG1pbi9cIn0pO1xuICB3aW5kb3cuZXZlbnRCdXMgPSBfLmNsb25lKEJhY2tib25lLkV2ZW50cyk7XG4gIHdpbmRvdy5ldmVudEJ1cy5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihtc2cpe1xuICAgIGFwcFJvdXRlci5uYXZpZ2F0ZShtc2csIHt0cmlnZ2VyOiB0cnVlfSk7XG4gIH0pXG59KTtcblxuIiwiXG5leHBvcnQgY29uc3QgSW5kZXhNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKCl7XG4gICAgcmV0dXJuICcvYWRtaW4vZGFzaGJvYXJkJztcbiAgfVxufSk7XG4iLCJcbmV4cG9ydCBjb25zdCBJdGVtQ29sbGVjdGlvbk1vZGVsID0gQmFja2JvbmUuTW9kZWwuZXh0ZW5kKHtcbiAgdXJsIDogZnVuY3Rpb24oaWQpe1xuICAgIHJldHVybiAnL2FkbWluL2ljLycgKyB0aGlzLmdldCgnaWQnKTtcbiAgfVxufSk7XG4iLCJcbmV4cG9ydCBjb25zdCBPcmdNb2RlbCA9IEJhY2tib25lLk1vZGVsLmV4dGVuZCh7XG4gIHVybCA6IGZ1bmN0aW9uKG5hbWUpe1xuICAgIGNvbnNvbGUubG9nKHRoaXMuZ2V0KCduYW1lJykpO1xuICAgIHJldHVybiAnL2FkbWluL28vJyArIHRoaXMuZ2V0KCduYW1lJyk7XG4gIH1cbn0pO1xuIiwiZXhwb3J0IGNvbnN0IEluZGV4VGVtcGxhdGUgPSBgXG4gIHt7I29yZ3N9fVxuICAgIDxhIGhyZWY9XCJqYXZhc2NyaXB0OnZvaWQoMClcIiBvbi1jbGljaz1cIm5hdmlnYXRlXCI+e3t0aXRsZX19PC9hPlxuICB7ey99fVxuYFxuIiwiZXhwb3J0IGNvbnN0IEl0ZW1Db2xsZWN0aW9uVGVtcGxhdGUgPSBgXG4gIHt7I2l0ZW1zfX1cbiAgICA8aDM+e3t0aXRsZX19PC9oMz5cbiAge3svfX1cbmBcbiIsImV4cG9ydCBjb25zdCBvcmdUZW1wbGF0ZSA9IGBcbiAgPHA+SGVsbG8sIHt7bmFtZX19ITwvcD5cbiAge3sjaXRlbV9jb2xsZWN0aW9uc319XG4gICAgPGgzPnt7bmFtZX19PC9oMz5cbiAge3svfX1cbmBcbiIsIlxuaW1wb3J0IHtJbmRleE1vZGVsfSBmcm9tICcuLi9tb2RlbHMvaW5kZXguanMnO1xuaW1wb3J0IHtJbmRleFRlbXBsYXRlfSBmcm9tICcuLi90ZW1wbGF0ZXMvaW5kZXguaHRtbC5qcyc7XG5cbmV4cG9ydCBjb25zdCBJbmRleFZpZXcgPSB7XG4gIHJlbmRlcjogZnVuY3Rpb24oKSB7XG4gICAgY29uc29sZS5sb2coIXRoaXMucmFjdGl2ZSk7XG4gICAgaWYgKCF0aGlzLmluZGV4TW9kZWwpIHtcbiAgICAgIHRoaXMuaW5kZXhNb2RlbCA9IG5ldyBJbmRleE1vZGVsKCk7XG4gICAgfVxuICAgIHRoaXMuaW5kZXhNb2RlbC5mZXRjaCgpLnRoZW4oZnVuY3Rpb24oZGF0YSl7XG4gICAgICBpZiAoIXRoaXMucmFjdGl2ZSkge1xuICAgICAgICBjb25zb2xlLmxvZyhcInJhY3RpdmVcIilcbiAgICAgICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgICAgICB0ZW1wbGF0ZTogSW5kZXhUZW1wbGF0ZSxcbiAgICAgICAgICBkYXRhOiB7XG4gICAgICAgICAgICBvcmdzOiBkYXRhLm9yZ3NcbiAgICAgICAgICB9XG4gICAgICAgIH0pO1xuICAgICAgICB0aGlzLnJhY3RpdmUub24oJ25hdmlnYXRlJywgZnVuY3Rpb24oZXZlbnQsIG1ldGhvZCl7XG4gICAgICAgICAgLy8gY29uc29sZS5sb2coZXZlbnQuY29udGV4dC51cmwpO1xuICAgICAgICAgIGV2ZW50QnVzLnRyaWdnZXIoJ25hdmlnYXRlJywgZXZlbnQuY29udGV4dC51cmwpO1xuICAgICAgICB9KTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHRoaXMucmFjdGl2ZS5yZW5kZXIoKTtcbiAgICAgIH1cbiAgICB9KVxuICB9XG59XG4iLCJcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25Nb2RlbH0gZnJvbSAnLi4vbW9kZWxzL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5pbXBvcnQge0l0ZW1Db2xsZWN0aW9uVGVtcGxhdGV9IGZyb20gJy4uL3RlbXBsYXRlcy9pdGVtX2NvbGxlY3Rpb24uaHRtbC5qcyc7XG5cbmV4cG9ydCBjb25zdCBJdGVtQ29sbGVjdGlvblZpZXcgPSB7XG4gIHJlbmRlcjogZnVuY3Rpb24oaW5pdERhdGEpIHtcbiAgICBjb25zb2xlLmxvZyghdGhpcy5yYWN0aXZlKTtcbiAgICBpZiAoIXRoaXMubW9kZWwpIHtcbiAgICAgIHRoaXMubW9kZWwgPSBuZXcgSXRlbUNvbGxlY3Rpb25Nb2RlbCh7XG4gICAgICAgIGlkOiBpbml0RGF0YS5pZFxuICAgICAgfSk7XG4gICAgfVxuICAgIHRoaXMubW9kZWwuZmV0Y2goKS50aGVuKGZ1bmN0aW9uKGRhdGEpe1xuICAgICAgaWYgKCF0aGlzLnJhY3RpdmUpIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgICAgICB0ZW1wbGF0ZTogSXRlbUNvbGxlY3Rpb25UZW1wbGF0ZSxcbiAgICAgICAgICBkYXRhOiB7XG4gICAgICAgICAgICBpdGVtczogZGF0YS5pdGVtc1xuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICAgIHRoaXMucmFjdGl2ZS5vbignbmF2aWdhdGUnLCBmdW5jdGlvbihldmVudCwgbWV0aG9kKXtcbiAgICAgICAgICAvLyBjb25zb2xlLmxvZyhldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgICAgZXZlbnRCdXMudHJpZ2dlcignbmF2aWdhdGUnLCBldmVudC5jb250ZXh0LnVybCk7XG4gICAgICAgIH0pO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlLnJlbmRlcigpO1xuICAgICAgfVxuICAgIH0pXG4gIH1cbn1cbiIsIlxuaW1wb3J0IHtPcmdNb2RlbH0gZnJvbSAnLi4vbW9kZWxzL29yZy5qcyc7XG4vLyBpbXBvcnQge3JlbmRlcnZpZXd9IGZyb20gJy4vcmVuZGVydmlldy5qcyc7XG5pbXBvcnQge29yZ1RlbXBsYXRlfSBmcm9tICcuLi90ZW1wbGF0ZXMvb3JnLmh0bWwuanMnO1xuXG5leHBvcnQgY29uc3QgT3JnVmlldyA9IHtcbiAgcmVuZGVyOiBmdW5jdGlvbihvcmcpIHtcbiAgICBpZiAoIXRoaXMub3JnTW9kZWwpIHtcbiAgICAgIHRoaXMub3JnTW9kZWwgPSBuZXcgT3JnTW9kZWwoe1xuICAgICAgICBuYW1lOiBvcmcubmFtZVxuICAgICAgfSk7XG4gICAgfVxuICAgIHRoaXMub3JnTW9kZWwuZmV0Y2goKS50aGVuKGZ1bmN0aW9uKGRhdGEpe1xuICAgICAgaWYgKCF0aGlzLnJhY3RpdmUpIHtcbiAgICAgICAgdGhpcy5yYWN0aXZlID0gbmV3IFJhY3RpdmUoe1xuICAgICAgICAgIGVsOiAnI21haW4tY29udGVudC1hcmVhJyxcbiAgICAgICAgICAvLyB0ZW1wbGF0ZTogJyNvcmctY29udGVudC10ZW1wbGF0ZScsXG4gICAgICAgICAgdGVtcGxhdGU6IG9yZ1RlbXBsYXRlLFxuICAgICAgICAgIGRhdGE6IHtcbiAgICAgICAgICAgIG5hbWU6IGRhdGEubmFtZSxcbiAgICAgICAgICAgIGl0ZW1fY29sbGVjdGlvbnM6IGRhdGEuaXRlbV9jb2xsZWN0aW9uc1xuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICB0aGlzLnJhY3RpdmUucmVuZGVyKCk7XG4gICAgICB9XG4gICAgfSk7XG5cbiAgfVxufVxuIiwiXG5pbXBvcnQge0luZGV4Vmlld30gZnJvbSAnLi9pbmRleC5qcyc7XG5pbXBvcnQge09yZ1ZpZXd9IGZyb20gJy4vb3JnLmpzJztcbmltcG9ydCB7SXRlbUNvbGxlY3Rpb25WaWV3fSBmcm9tICcuL2l0ZW1fY29sbGVjdGlvbi5qcyc7XG5cbmV4cG9ydCBjb25zdCBSb3V0ZXIgPSBCYWNrYm9uZS5Sb3V0ZXIuZXh0ZW5kKHtcbiAgcm91dGVzOiB7XG4gICAgXCJcIjogXCJpbmRleFwiLFxuICAgIFwiby86b3JnXCI6IFwib3JnXCIsXG4gICAgXCJpYy86aWNJZFwiOiBcIml0ZW1fY29sbGVjdGlvblwiXG4gIH0sXG4gIGluZGV4OiBmdW5jdGlvbigpIHtcbiAgICBJbmRleFZpZXcucmVuZGVyKCk7XG4gIH0sXG4gIG9yZzogZnVuY3Rpb24ob3JnKXtcbiAgICBPcmdWaWV3LnJlbmRlcih7bmFtZTogb3JnfSk7XG4gIH0sXG4gIGl0ZW1fY29sbGVjdGlvbjogZnVuY3Rpb24oaWNJZCl7XG4gICAgSXRlbUNvbGxlY3Rpb25WaWV3LnJlbmRlcih7aWQ6IGljSWR9KTtcbiAgfVxufSk7XG4iXX0=
