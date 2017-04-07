# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Popular(models.Model):
	GENERAL = 'GN'
	COLOMBIAN = 'CO'
	TYPE_CHOICES = (
		(GENERAL, 'General'),
		(COLOMBIAN, 'Colombian'),
	)
	repo_name = models.CharField(max_length=200)
	stars = models.IntegerField(default=0)
	sort = models.IntegerField(default=0)
	type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=GENERAL,
    )

	def __str__(self):
		return str(self.sort) + ' ' + self.repo_name + ' ' + self.type + ' ' + str(self.stars)

	class Meta:
		ordering = ['type', 'sort']


class Collaborator(models.Model):
    repo_name = models.CharField(max_length=200)
    repo_description = models.CharField(max_length=200)
    sort = models.IntegerField(default=0)
    collaborators = models.IntegerField(default=0)

    def __str__(self):
    	return self.repo_name + str(self.collaborators)

	class Meta:
		ordering = ['sort']