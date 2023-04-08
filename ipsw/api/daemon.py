class DaemonApiMixin:
    # def events(self, since=None, until=None, filters=None, decode=None):
    #     """
    #     Get real-time events from the server. Similar to the ``ipsw events``
    #     command.

    #     Args:
    #         since (UTC datetime or int): Get events from this point
    #         until (UTC datetime or int): Get events until this point
    #         filters (dict): Filter the events by event time, container or image
    #         decode (bool): If set to true, stream will be decoded into dicts on
    #             the fly. False by default.

    #     Returns:
    #         A :py:class:`ipsw.types.daemon.CancellableStream` generator

    #     Raises:
    #         :py:class:`ipsw.errors.APIError`
    #             If the server returns an error.

    #     Example:

    #         >>> for event in client.events(decode=True)
    #         ...   print(event)
    #         {u'from': u'image/with:tag',
    #          u'id': u'container-id',
    #          u'status': u'start',
    #          u'time': 1423339459}
    #         ...

    #         or

    #         >>> events = client.events()
    #         >>> for event in events:
    #         ...   print(event)
    #         >>> # and cancel from another thread
    #         >>> events.close()
    #     """

    #     if isinstance(since, datetime):
    #         since = utils.datetime_to_timestamp(since)

    #     if isinstance(until, datetime):
    #         until = utils.datetime_to_timestamp(until)

    #     if filters:
    #         filters = utils.convert_filters(filters)

    #     params = {
    #         'since': since,
    #         'until': until,
    #         'filters': filters
    #     }
    #     url = self._url('/events')

    #     response = self._get(url, params=params, stream=True, timeout=None)
    #     stream = self._stream_helper(response, decode=decode)

    #     return types.CancellableStream(stream, response)

    def ping(self):
        """
        Checks the server is responsive. An exception will be raised if it
        isn't responding.

        Returns:
            (bool) The response from the server.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url('/_ping'))) == 'OK'

    def version(self, api_version=True):
        """
        Returns version information from the server. Similar to the ``ipsw
        version`` command.

        Returns:
            (dict): The server version information

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        url = self._url("/version", versioned_api=api_version)
        return self._result(self._get(url), json=True)
