"""
Define `FilingsPage` class.

"""

# SPDX-FileCopyrightText: 2023-present Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from itertools import chain
import warnings

from ..api_request import APIRequest
from ..enums import (
    ScopeFlag, GET_ONLY_FILINGS, GET_ENTITY, GET_VALIDATION_MESSAGES)
from ..exceptions import ApiIdCoherenceWarning
from ..exceptions import ApiReferenceWarning
from ..filing_set.resource_collection import ResourceCollection
from .api_page import APIPage
from .api_resource import APIResource
from .entity import Entity
from .filing import Filing
from .validation_message import ValidationMessage


class FilingsPage(APIPage):
    """
    JSON:API response page containing filing resources.
    
    Attributes
    ----------
    request_time : datetime
    query_filing_count : int or None
    filing_list: list of Filing
    entity_list : list of Entity or None
    validation_message_list : list of ValidationMessage or None
    jsonapi_version : str or None
    api_self_url : str or None
    api_prev_page_url : str or None
    api_next_page_url : str or None
    api_first_page_url : str or None
    api_last_page_url : str or None
    request_url : str
    """
    def __init__(
            self, json_frag: dict, api_request: APIRequest,
            flags: ScopeFlag, received_api_ids: dict[str, set],
            res_colls: dict[str, ResourceCollection]
            ) -> None:
        """Initiate a JSON:API response page.

        Warns
        -----
        ApiReferenceWarning
            Resource referencing between filings, entities and
            validation messages fails.
        """
        super().__init__(json_frag, api_request)

        self.query_filing_count = self._data_count
        """Total count of filings of the query including the ones not on
        this page.
        """

        self.filing_list: list[Filing]
        """List of `Filing` objects on this page."""

        self.entity_list: list[Entity] | None = (
            self._get_inc_entity(
                api_request=api_request,
                received_api_ids=received_api_ids,
                type_obj=Entity,
                flag_member=GET_ENTITY,
                flags=flags
                ))
        """
        Set of `Entity` objects on this page.
        
        Is `None` if `flags` parameter did not include `GET_ENTITY`.
        """
        
        self.validation_message_list: list[ValidationMessage] | None = (
            self._get_inc_validation_message(
                api_request=api_request,
                received_api_ids=received_api_ids,
                type_obj=ValidationMessage,
                flag_member=GET_VALIDATION_MESSAGES,
                flags=flags
                ))
        """
        Set of `ValidationMessage` objects on this page.

        Is `None` if `flags` parameter did not include
        `GET_VALIDATION_MESSAGES`.
        """
        
        self._json.close()

        self.filing_list = self._get_filings(
            received_api_ids, res_colls, flags)
        self._check_validation_messages_references()
        self._determine_unexpected_inc_resources()
    
    def _get_filings(
            self, received_api_ids: dict[str, set],
            res_colls: dict[str, ResourceCollection], flags: ScopeFlag
            ) -> list[Filing]:
        """Get filings from from `data` key.

        Warns
        -----
        ApiReferenceWarning
        """
        filing_list = []
        if not received_api_ids.get('Filing'):
            received_api_ids['Filing'] = set()
        received_set = received_api_ids['Filing']

        if self._data:
            for res_frag in self._data:
                res_type = str(res_frag.get('type')).lower()

                if res_type == Filing.TYPE:
                    res_id = str(res_frag.get('id'))
                    if res_id in received_set:
                        msg = (
                            f'Same filing returned again, api_id={res_id!r}.'
                            )
                        warnings.warn(msg, ApiIdCoherenceWarning)
                    else:
                        received_set.add(res_id)
                        entity_iter = None
                        message_iter = None
                        if GET_ONLY_FILINGS not in flags:
                            if GET_ENTITY in flags:
                                entity_iter = chain(
                                    self.entity_list,
                                    res_colls['Entity']
                                    )
                            if GET_VALIDATION_MESSAGES in flags:
                                message_iter = chain(
                                    self.validation_message_list,
                                    res_colls['ValidationMessage']
                                    )
                        filing = Filing(
                            res_frag,
                            APIRequest(self.request_url, self.request_time),
                            entity_iter,
                            message_iter
                            )
                        filing_list.append(filing)
                else:
                    self._json.unexpected_resource_types.add(
                        (res_type, 'data'))
        return filing_list

    def _get_inc_resource(
            self,
            api_request: APIRequest,
            received_api_ids: dict[str, set],
            type_obj: type[APIResource],
            flag_member: ScopeFlag,
            flags: ScopeFlag
            ) -> list[Entity | ValidationMessage] | None:
        if (GET_ONLY_FILINGS in flags or flag_member not in flags):
            return None
        
        resource_list = []
        type_name = type_obj.__class__.__name__
        if not received_api_ids.get(type_name):
            received_api_ids[type_name] = set()
        received_set = received_api_ids[type_name]

        found_ix = []
        for res_i, res in enumerate(self._included_resources):
            if res.type == type_obj.TYPE:
                if res.id not in received_set:
                    received_set.add(res.id)
                    # Construct Entity() or ValidationMessage()
                    res_instance = type_obj(res.frag, api_request)
                    resource_list.append(res_instance)
                    found_ix.append(res_i)
        found_ix.reverse()
        for res_i in found_ix:
            del self._included_resources[res_i]
        return resource_list
    
    def _get_inc_entity(self, **kwargs) -> list[Entity] | None:
        reslist = self._get_inc_resource(**kwargs)
        if reslist is None:
            return None
        ents = [
            res for res in reslist
            if isinstance(res, Entity)
            ]
        return ents
    
    def _get_inc_validation_message(self, **kwargs) -> list[ValidationMessage] | None:
        reslist = self._get_inc_resource(**kwargs)
        if reslist is None:
            return None
        vmsgs = [
            res for res in reslist
            if isinstance(res, ValidationMessage)
            ]
        return vmsgs
    
    def _determine_unexpected_inc_resources(self) -> None:
        self._json.unexpected_resource_types.update(
            [(res.type, 'included') for res in self._included_resources])
    
    def _check_validation_messages_references(self) -> None:
        if self.validation_message_list is not None:
            for vmsg in self.validation_message_list:
                if vmsg.filing is None:
                    msg = (
                        f'No filing defined for {vmsg!r}, api_id={vmsg.api_id}'
                        )
                    warnings.warn(msg, ApiReferenceWarning, stacklevel=2)
