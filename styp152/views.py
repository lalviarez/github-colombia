# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from google.cloud import bigquery

from .models import Popular, Collaborator

import time
import uuid

def wait_for_job(job):
    while True:
        job.reload()  # Refreshes the state via a GET request.
        if job.state == 'DONE':
            if job.error_result:
                raise RuntimeError(job.errors)
            return
        time.sleep(1)


def async_query(query):
    client = bigquery.Client()
    query_job = client.run_async_query(str(uuid.uuid4()), query)
    query_job.use_legacy_sql = False
    query_job.begin()

    wait_for_job(query_job)

    query_results = query_job.results()
    page_token = None
    results = []

    while True:
        rows, total_rows, page_token = query_results.fetch_data(
            max_results=10,
            page_token=page_token)

        for row in rows:
            results.append(row)

        if not page_token:
            break

    return results

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'popular_items_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Popular.objects.filter(type='GN')

    def get_context_data(self, *args, **kwargs):
       context = super(IndexView, self).get_context_data(*args, **kwargs)
       context['colombians_items_list'] = Popular.objects.filter(type='CO')
       context['collaborators_items_list'] = Collaborator.objects.all()
       return context 

def load(request):

	Popular.objects.all().delete()
	Collaborator.objects.all().delete()

	populars = async_query(""" 
		SELECT repo.id repo_id,  COUNT(DISTINCT actor.login) stars, APPROX_TOP_COUNT(repo.name, 1)[OFFSET(0)].value name
		FROM `githubarchive.year.*` stars
		JOIN `ghtorrent-bq.ght_2017_01_19.users` users 
		ON stars.actor.login= users.login
		AND stars.type='WatchEvent'
		WHERE repo.id IS NOT null
		GROUP BY repo_id ORDER BY stars DESC LIMIT 10;""")

	i = 0
	while i < len(populars):
	    popular = Popular(repo_name=populars[i][2], stars=populars[i][1], sort=i+1, type='GN')
	    popular.save()
	    i+=1

	populars_colombia = async_query(""" 
		SELECT populars.name, stars FROM 
  		(SELECT repo.id repo_id,  COUNT(DISTINCT actor.login) stars, APPROX_TOP_COUNT(repo.name, 1)[OFFSET(0)].value name
      	FROM `githubarchive.year.*` stars
      	JOIN `ghtorrent-bq.ght_2017_01_19.users` users 
      	ON stars.actor.login= users.login
      	AND stars.type='WatchEvent'
      	WHERE repo.id IS NOT null
      	GROUP BY repo_id
      	ORDER BY stars DESC ) populars
  		JOIN ( SELECT project_id FROM `ghtorrent-bq.ght_2017_01_19.users` users 
    	JOIN `ghtorrent-bq.ght_2017_01_19.commits` commits ON commits.author_id = users.id 
    	WHERE location LIKE '%Colombia%' OR location LIKE '%colombia%' AND users.deleted IS NOT true 
    	GROUP BY project_id
    	ORDER BY project_id ) colombians 
  		ON populars.repo_id = colombians.project_id
  		ORDER BY stars DESC
  		LIMIT 10;""")

	i = 0
	while i < len(populars_colombia):
		popular = Popular(repo_name=populars_colombia[i][0], stars=populars_colombia[i][1], sort=i+1, type='CO')
		popular.save()
		i+=1

	collaborators_colombia = async_query(""" 
		SELECT collaborators.project_id, collaborators.number, repos.name, repos.url, repos.description FROM (
  		SELECT project_id, COUNT(DISTINCT users.id) number FROM `ghtorrent-bq.ght_2017_01_19.users` users 
    	JOIN `ghtorrent-bq.ght_2017_01_19.commits` commits ON commits.author_id = users.id 
    	WHERE location LIKE '%Colombia%' OR location LIKE '%colombia%' AND users.deleted IS NOT true 
    	GROUP BY project_id
    	ORDER BY number DESC, project_id ) collaborators
  		JOIN `ghtorrent-bq.ght_2017_01_19.projects` repos ON repos.id = collaborators.project_id 
  		ORDER BY collaborators.number DESC LIMIT 10;""")

	i = 0
	while i < len(collaborators_colombia):
		collaborator = Collaborator(repo_name=collaborators_colombia[i][2], repo_description=collaborators_colombia[i][4], sort=i+1, collaborators=collaborators_colombia[i][1])
		collaborator.save()
		i+=1

	return redirect('index')