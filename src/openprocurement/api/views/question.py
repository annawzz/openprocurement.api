# -*- coding: utf-8 -*-
from cornice.resource import resource, view
from openprocurement.api.models import Question
from openprocurement.api.utils import (
    apply_data_patch,
    save_tender,
)
from openprocurement.api.validation import (
    validate_question_data,
    validate_patch_question_data,
)


@resource(name='Tender Questions',
          collection_path='/tenders/{tender_id}/questions',
          path='/tenders/{tender_id}/questions/{question_id}',
          description="Tender questions")
class TenderQuestionResource(object):

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db

    @view(content_type="application/json", validators=(validate_question_data,), permission='view_tender', renderer='json')
    def collection_post(self):
        """Post a question
        """
        tender = self.request.validated['tender']
        question_data = self.request.validated['data']
        question = Question(question_data)
        src = tender.serialize("plain")
        tender.questions.append(question)
        save_tender(tender, src, self.request)
        self.request.response.status = 201
        self.request.response.headers['Location'] = self.request.route_url('Tender Questions', tender_id=tender.id, question_id=question['id'])
        return {'data': question.serialize("view")}

    @view(renderer='json', permission='view_tender')
    def collection_get(self):
        """List questions
        """
        return {'data': [i.serialize(self.request.validated['tender'].status) for i in self.request.validated['tender'].questions]}

    @view(renderer='json', permission='view_tender')
    def get(self):
        """Retrieving the question
        """
        return {'data': self.request.validated['question'].serialize(self.request.validated['tender'].status)}

    @view(content_type="application/json", permission='edit_tender', validators=(validate_patch_question_data,), renderer='json')
    def patch(self):
        """Post an Answer
        """
        tender = self.request.validated['tender']
        question = self.request.validated['question']
        question_data = self.request.validated['data']
        if question_data:
            src = tender.serialize("plain")
            question.import_data(apply_data_patch(question.serialize(), question_data))
            save_tender(tender, src, self.request)
        return {'data': question.serialize(tender.status)}
