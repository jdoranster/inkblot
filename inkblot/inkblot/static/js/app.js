window.App = App =  Ember.Application.create({
            LOG_TRANSITIONS: true,
          });

App.Adapter = DS.RESTAdapter.extend();


//App.Adapter.map('App.Lesson', {
//  tasks: {'embedded': 'always'}
//});

App.Store = DS.Store.extend({
  revision: 12,
  //adapter: 'DS.FixtureAdapter'
  adapter: App.Adapter.extend({
  //adapter: DS.RESTAdapter.create({
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
});

// selects default tab when page loads
App.IndexRoute = Ember.Route.extend({
  redirect: function () {
    this.transitionTo('lessons');
  }
});

App.User = DS.Model.extend({
  
});

App.Lesson = DS.Model.extend({
  tasks: DS.hasMany('App.Task'),
  title: DS.attr('string'),
  instruction: DS.attr('string'),
  ltype: DS.attr('string'),

});

App.Task = DS.Model.extend({
  lesson: DS.belongsTo('App.Lesson'),
  word: DS.attr('string'),
  sound: DS.attr('string'),
});


App.LessonsRoute = Ember.Route.extend({
  model: function() {
    return App.Lesson.find();
    }
});



App.TaskView = Ember.View.extend ({
  templateName: 'task-view',
  attributeBindings: ['task-id','task-sound', 'task-word'],
  'task-id': function() {
        return this.content.id;
  }.property('content.id'),
  'task-sound': function() {
        return this.content.sound;
  }.property('content.sound'),
  'task-word': function() {
        return this.content.word;
  }.property('content.word'),
    
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




App.Lesson.FIXTURES = [{
  id: 1,
  title: 'Lesson 1',
  instruction: 'Press the image and hear the phoneme',
},{
  id: 2,
  title: 'Lesson 2',
  instruction: 'Press the combinations to create words',
}];
