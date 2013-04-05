App = Ember.Application.create();

App.Store = DS.Store.extend({
  revision: 12,
  //adapter: 'DS.FixtureAdapter'
  adapter: DS.RESTAdapter.extend({
    url: 'http://localhost:6543/test'
  })
});

App.Router.map(function() {
  // put your routes here
  this.resource('lessons', function (){
    this.resource('lesson', { path: ':lesson_id'})
  });
  this.resource('about');
});

App.IndexRoute = Ember.Route.extend({
  redirect: function () {
    this.transitionTo('lessons');
  }
});

App.Task = DS.Model.extend({
  lesson: DS.belongsTo('App.Lesson'),
  notes: DS.attr('string'),
  
});

App.Lesson = DS.Model.extend({
  tasks: DS.hasMany('App.Task'),
  title: DS.attr('string'),
  instruction: DS.attr('string'),
});

App.LessonsRoute = Ember.Route.extend({
  model: function() {
    return App.Lesson.find();
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
