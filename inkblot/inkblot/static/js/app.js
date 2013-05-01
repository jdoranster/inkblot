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
  prompt: DS.attr('string'),
  result: DS.attr('string'),
});


App.LessonsRoute = Ember.Route.extend({
  model: function() {
    return App.Lesson.find();
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




App.Lesson.FIXTURES = [{
  id: 1,
  title: 'Lesson 1',
  instruction: 'Press the image and hear the phoneme',
},{
  id: 2,
  title: 'Lesson 2',
  instruction: 'Press the combinations to create words',
}];
