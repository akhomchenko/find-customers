# coding: utf-8


import sys
import math
import operator
import functools
import collections

import click
import simplejson

__all__ = ('EARTH_RADIUS', 'Location', 'Customer', 'great_circle_distance',
           'cli')

EARTH_RADIUS = 6371.2


class CustomerParsingError(BaseException):
    """
    Raised when customer is failed to be parsed
    """


Location = collections.namedtuple('Location', ['lat', 'lon'])
Customer = collections.namedtuple('Customer', ['id', 'name', 'location'])


def great_circle_distance(first, second):
    """
    Returns great-circle-distance in km.

    Based on https://en.wikipedia.org/wiki/Great-circle_distance

    :param first: instance of `Location` or `tuple(lat, lon)`
    :param second: instance of `Location` or `tuple(lat, lon)`
    """
    if isinstance(first, collections.Sequence):
        first = Location(*first[:2])
    if isinstance(second, collections.Sequence):
        second = Location(*second[:2])

    lat1, lon1 = math.radians(first.lat), math.radians(first.lon)
    lat2, lon2 = math.radians(second.lat), math.radians(second.lon)

    delta = lon2 - lon1

    sin_lat1, sin_lat2 = math.sin(lat1), math.sin(lat2)
    cos_lat1, cos_lat2 = math.cos(lat1), math.cos(lat2)
    cos_delta, sin_delta = math.cos(delta), math.sin(delta)

    d = math.atan2(math.sqrt((cos_lat2 * sin_delta) ** 2 +
                             (cos_lat1 * sin_lat2 -
                              sin_lat1 * cos_lat2 * cos_delta) ** 2),
                   sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta)

    return EARTH_RADIUS * d


def parse_customer(string):
    """
    Parses JSON representation of customer from `string`

    Expected structure is {`user_id`, `name`, `latitude`, `longitude`}

    Raises `CustomerParsingError` if failed to read customer

    :return: Customer
    """
    try:
        dct = simplejson.loads(string)
        return Customer(dct['user_id'], dct['name'], Location(
            float(dct['latitude']), float(dct['longitude'])))
    except (ValueError, KeyError, simplejson.JSONDecodeError):
        raise CustomerParsingError('Failed to parse: "{0}"'.format(string))


def find_closest_customers(customers, distance, center):
    """
    Returns iterator of customers that are at `distance` or closer to `center`

    :param customers: iterable of
    :param distance: number in km
    :param center: tuple of (lat, lon)
    """
    distance_to = functools.partial(great_circle_distance, center)
    close_enough = lambda customer: distance_to(customer.location) <= distance

    return (customer for customer in customers if close_enough(customer))


@click.command()
@click.argument('file', type=click.File('r'))
@click.option('-d', '--distance', 'distance', default=100.0,
              help='Distance in km that is good to match. Defaults to 100.0 km')
@click.option('-c', '--center', 'center', default=(53.3381985, -6.2592576),
              help='Point distance to which is calculated. '
                   'Defaults to Dublin office')
def cli(file, distance, center):
    """
    Finds customers within specified range near specified point
    """
    customers = (parse_customer(line.rstrip())
                 for line in file if not line.isspace())
    matching_customers = find_closest_customers(customers, distance=distance,
                                                center=center)

    try:
        for customer in sorted(matching_customers,
                               key=operator.attrgetter('id')):
            click.echo('{name} ({id})'.format(name=customer.name,
                                              id=customer.id))
    except CustomerParsingError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
