from django.urls import path
from .views import TaskListViewA, ChartData, HomeView, TeamTaskCreateView, TeamDeleteView, TeamUpdateView, TeamCreateView, TeamDetailView, TeamListView, TaskDeleteView, TaskUpdateView, TaskListView, UserTaskListView, TaskDetailView, TaskCreateView
from . import views

urlpatterns = [
    path('', TaskListView.as_view(), name='todo_list-personal'),
    path('manage/', TaskListViewA.as_view(), name='todo_list-manage'),
    path('user/<str:username>/', UserTaskListView.as_view(), name='user-tasks'),
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('team/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('task/new/', TaskCreateView.as_view(), name='task-create'),


    path('teamtask/new/', TeamTaskCreateView.as_view(), name='team-task-create'),
    path('assign/<int:task_id>/', views.assigner, name='team-assigner'),
    path('assignemail/<int:id>/', views.assignmentEmail, name='assign-email'),

    path('team/new/', TeamCreateView.as_view(), name='team-create'),
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('team/<int:pk>/update/', TeamUpdateView.as_view(), name='team-update'),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('team/<int:pk>/delete/', TeamDeleteView.as_view(), name='team-delete'),
    path('team/',TeamListView.as_view(), name='todo_list-team'),
    path('complete/<todo_id>/', views.completeTodo, name='complete'),
    path('complete2/<todo_id>/<main_id>/', views.completeTodo2, name='complete2'),
    path('accept/<todo_id>/', views.acceptTodo, name='accept'),
    path('todo/<todo_id>/', views.doTodo, name='todo'),
    path('todo2/<todo_id>/<main_id>/', views.doTodo2, name='todo2'),
    path('task/<todo_id>/subtask/', views.subtaskView, name='task-subtask'),
    path('email/', views.emailer, name='email'),

]

#app/model_viewtype.html