window.App = App =  Ember.Application.create({
            LOG_TRANSITIONS: true,
          });

//App.Adapter = DS.RESTAdapter.extend();


//App.Adapter.map('App.Lesson', {
//  tasks: {'embedded': 'always'}
//});

App.Store = DS.Store.extend({
  revision: 12,
  //adapter: 'DS.FixtureAdapter'
  //adapter: App.Adapter.extend({
  //adapter: DS.RESTAdapter.create({
  adapter: Auth.RESTAdapter.create({
    url: 'http://localhost:6543/test'
  })
});

//App.Store.adapter.serializer.map('App.Lesson', {
//   tasks: {embedded: 'load'}
//});


App.Router.map(function() {
  // put your routes here
  this.resource('lessons', { path: '/lessons'}, function() {
    this.resource('lesson', { path: ':lesson_id'}, function() {
      this.resource('tasks');     
    });
  });
  this.resource('about');
  this.resource('sign_in');
  this.resource('sign_out');
  this.resource('new_user');
});

// selects default tab when page loads
App.IndexRoute = Ember.Route.extend({
  redirect: function () {
    this.transitionTo('lessons');
  }
});


App.ApplicationController = Ember.Controller.extend({


  activeHome: (function() {
      return this.get('currentRoute') === 'home';
  }).property('currentRoute'),

  activeSignUp: (function() {
      return this.get('currentRoute') === 'sign_up';
  }).property('currentRoute'),

  activeUsers: (function() {
      return this.get('currentRoute') === 'users';
  }).property('currentRoute'),

  activeSignIn: (function() {
      return this.get('currentRoute') === 'sign_in';
  }).property('currentRoute'),


});

App.Lesson = DS.Model.extend({
  tasks: DS.hasMany('App.Task'),
  title: DS.attr('string'),
  instruction: DS.attr('string'),
  ltype: DS.attr('string'),

});

App.Task = DS.Model.extend({
  lesson: DS.belongsTo('App.Lesson'),
  prompt: DS.attr('string'),
  result: DS.attr('string'),
});


App.LessonsRoute = Ember.Route.extend({
  model: function() {
    return App.Lesson.find();
    }
});

App.LessonsView = Ember.View.extend ({
  templateName: 'lessons',
  
  contentChange: function() {
      this.rerender();
      }
});

App.LessonController = Ember.ObjectController.extend({
  rows: function() {
    var rows = []; //This is the array of rows with tasks that we will return
    const ROWMAX = 2;
    var currow = [];
    this.get('content.tasks').forEach(function(task) {
      if (currow.length % ROWMAX == 0) {
        if (currow.length != 0) {
          rows.push(currow);
        }
        currow = [];
      }
      currow.push(task);
    });
    if (currow.length != 0) {
      rows.push(currow);
    }
    return rows;
  }.property('tasks.@each', 'tasks.@each.isLoaded'),
  

});

Handlebars.registerHelper('newrow', function(idx, rowmax, options) {
              /*var idx = view.contentIndex;*/
              var index = Ember.get(this, idx);
              if (index != 0  && index % rowmax === 0)
                return options.fn(this);

});  



App.TasksView = Ember.View.extend({
  templateName: 'tasks-view',
  tasksWithIndices: function() {
      return this.content.map(function(item, index) {
        return {task: item, idx: index};
      });
    }.property('tasks.@each', 'tasks.@each.task')

});

App.TaskView = Ember.View.extend ({
  templateName: 'task-view',
       
  click: function(evt) {

    var audios = $(evt.currentTarget).children().find('audio');
    if (audios.length > 0) {
        audios[0].play();
        $(evt.currentTarget).find('a').addClass('clicked')
        // TODO: store the info that this task was completed
    }
    return false;
  }

});





/* -----------   Auth stuff follows --------------- */

Auth.Config.reopen({
  urlAuthentication: true, //Used for Oauth callback 
  urlAuthenticationParamsKey: 'auth',
  urlAuthenticationRouteScope: 'both',
  tokenCreateUrl: '/user/sign_in',
  tokenDestroyUrl: 'user/sign_out',
  tokenKey: 'authToken',
  idKey: 'user_id',
  rememberMe: true,
  rememberTokenKey: 'remember_token',
  rememberPeriod: 14,
  rememberAutoRecall: true,
  rememberAutoRecallRouteScope: 'both',
  userModel: App.User,
  signInRoute: 'sign_in',
  authRedirect: true,
  smartSignInRedirect: true,
  signInRedirectFallbackRoute: 'lessons', 
  baseUrl: 'http://localhost:6543',
  requestTokenLocation: 'customHeader',
  requestHeaderKey: 'X-Messaging-Token',
});

App.User = DS.Model.extend({
  name: DS.attr('string'),
  email: DS.attr('string'),
  current_password: DS.attr('string'),
  password: DS.attr('string'),
  password_confirmation: DS.attr('string'),
  admin: DS.attr('boolean'),
  validationError: false,
  validationErrors: {},
  updated: false,
  
  becameError: function() {
    if (!this.get('isNew')) this.get('transaction').rollback();
    //this.rollback(); This doesn't work, you get becameClean error
    this.set('validationError',true);
    this.set('validationErrors', 'Error.');
  },
  becameInvalid: function(errors) {
    if (!this.get('isNew')) this.get('transaction').rollback();
    //this.rollback(); This doesn't work, you get becameClean error
    this.set('validationError',true);
    this.set('validationErrors', this.errors);
  },
  didUpdate: function() {
    this.set('updated',true);
  }
});

App.SignInRoute = Ember.Route.extend({
  setupController: function(controller, model) {
    this.controllerFor('application').set('currentRoute', 'sign_in');
  },
});


App.SignOutRoute = Ember.Route.extend({
  setupController: function(controller, model) {
    this.controllerFor('application').set('currentRoute', 'sign_out');
  },
});

App.SignUpRoute = Ember.Route.extend({
  setupController: function(controller, model) {
    this.controllerFor('application').set('currentRoute', 'sign_up');
  },
});


  
App.SignInController = Ember.ObjectController.extend(Auth.SignInController, {
  //needs: ["users_edit"],

  name: null,
  password: null,
  remember: false,
  loginError: false,
  loginResponse: "",
  signIn: function() {
    this.registerRedirect();
    Auth.signIn({
      name: this.get('name'),
      password: this.get('password'),
      remember: this.get('remember')
    });
    var self = this;
    Auth.on('signInError', function() {
      self.set('loginError', true);
      self.set('loginResponse', Auth.get('jqxhr').statusText);
    });
    Auth.on('signInSuccess', function() {
      self.set('loginError', false);
      App.Store.__super__.findQuery(App.Lesson, []);
    }); 
  },
  dismissError: function() {
    this.set('loginError', false);
  }
  });


App.SignInView = Ember.View.extend ({
  templateName: 'sign_in',
});



App.SignOutView = Ember.View.extend ({
  templateName: 'sign_out',
});


App.SignOutController = Ember.ObjectController.extend(Auth.SignOutController, {
  signOut: function() {
    this.registerRedirect();
    Auth.signOut();
    Auth.on('signOutSuccess', function() {
      $.removeCookie("X-Messaging-Token", {path:'/'});
      //App.Store.__super__.findQuery(App.Lesson, []);
      // Need to remove lessons as a 403 result does not update Data chache
      App.Lesson.all().forEach(function(model) {
        if (model){
          model.unloadRecord();
        }
      });
    }); 
  },

});

// Extend the Ember TextField to support additional HTML5 properties
App.TextField = Ember.TextField.extend({
    attributeBindings: ['accept', 'autocomplete', 'autofocus', 'name', 'required']
});



App.Lesson.FIXTURES = [{
  id: 1,
  title: 'Lesson 1',
  instruction: 'Press the image and hear the phoneme',
},{
  id: 2,
  title: 'Lesson 2',
  instruction: 'Press the combinations to create words',
}];