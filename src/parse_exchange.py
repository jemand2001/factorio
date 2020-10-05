from zlib import decompress, crc32
from base64 import decodebytes as decode
from typing import Union, Callable, Mapping, TypeVar, Hashable, Iterator, Any, Tuple, Dict
from functools import partial

from src.custom_types import byte, short, single, double, boolean

type_parsers = {}
K = TypeVar('K', bound=Hashable)
V = TypeVar('V')
T = TypeVar('T')


def type_parser(*types):
    def decorator(f):
        for type_ in types:
            type_parsers[type_] = f
        return f

    return decorator


def get_parser(type_, self):
    return partial(type_parsers[type_], self)


prototype_pollution = {
    "enabled": bool,
    "diffusion_ratio": double,
    "min_to_diffuse": double,
    "ageing": double,
    "expected_max_per_chunk": double,
    "min_to_show_per_chunk": double,
    "min_pollution_to_damage_trees": double,
    "pollution_with_max_forest_damage": double,
    "pollution_per_tree_damage": double,
    "pollution_restored_per_tree_damage": double,
    "max_pollution_to_restore_trees": double,
}
prototype_steering = {
    'a': double,
    'b': double,
    'separation_force': double,
    'force_unit_fuzzy_goto_behavior': bool
}
prototype_evolution = {
    'enabled': bool,
    'time_factor': double,
    'destroy_factor': double,
    'pollution_factor': double
}
prototype_expansion = {
    'enabled': boolean,
    'max_expansion_distance': int,
    'friendly_base_influence_radius': int,
    'enemy_building_influence_radius': int,
    'building_coefficient': double,
    'other_base_coefficient': double,
    'neighbouring_chunk_coefficient': double,
    'neighbouring_base_chunk_coefficient': double,
    'max_colliding_tiles_coefficient': double,
    'settler_group_min_size': int,
    'settler_group_max_size': int,
    'min_expansion_cooldown': int,
    'max_expansion_cooldown': int
}
prototype_group = {
    'min_group_gathering_time': int,
    'max_group_gathering_time': int,
    'max_wait_time_for_late_members': int,
    'max_group_radius': double,
    'min_group_radius': double,
    'max_member_speedup_when_behind': double,
    'max_member_slowdown_when_ahead': double,
    'max_group_slowdown_factor': double,
    'max_group_member_fallback_factor': double,
    'member_disown_distance': double,
    'tick_tolerance_when_member_arrives': int,
    'max_gathering_unit_groups': int,
    'max_unit_group_size': int
}
prototype_pathfinder = {
    'fwd2bwd_ratio': int,
    'goal_pressure_ratio': double,
    'use_path_cache': boolean,
    'max_steps_worked_per_tick': double,
    'short_cache_size': int,
    'long_cache_size': int,
    'short_cache_min_cacheable_distance': double,
    'short_cache_min_algo_steps_to_cache': int,
    'long_cache_min_cacheable_distance': double,
    'cache_max_connect_to_cache_steps_multiplier': int,
    'cache_accept_path_start_distance_ratio': double,
    'cache_accept_path_end_distance_ratio': double,
    'negative_cache_accept_path_start_distance_ratio': double,
    'negative_cache_accept_path_end_distance_ratio': double,
    'cache_path_start_distance_rating_multiplier': double,
    'cache_path_end_distance_rating_multiplier': double,
    'stale_enemy_with_same_destination_collision_penalty': double,
    'ignore_moving_enemy_collision_distance': double,
    'enemy_with_different_destination_collision_penalty': double,
    'general_entity_collision_penalty': double,
    'general_entity_subsequent_collision_penalty': double,
    'max_clients_to_accept_any_new_request': int,
    'max_clients_to_accept_short_new_request': int,
    'direct_distance_to_consider_short_request': int,
    'short_request_max_steps': int,
    'short_request_ratio': double,
    'min_steps_to_check_path_find_termination': int,
    'start_to_goal_cost_multiplier_to_terminate_path_find': double
}
prototype_difficulty = {
    'recipe': byte,
    'technology': byte,
    'technology_price_multiplier': double
}


class ExchangeStringParser:
    def __init__(self, exchange_string: Union[str, bytes]):
        if exchange_string[:3] != '>>>' or exchange_string[-3:] != '<<<':
            raise SyntaxError('invalid start or end')
        self.original = exchange_string
        exchange_string = exchange_string[3:-3].replace('\n', '')
        self.value = decompress(
            decode(
                exchange_string.encode()
                if isinstance(exchange_string, str)
                else exchange_string
            )
        )
        self.check()
        self.index = 0
        self.data = {}

    def __len__(self):
        return len(self.value)

    @type_parser(bool)
    def parse_bool(self) -> bool:
        return self.get_and_increment() == 1

    @type_parser(byte)
    def parse_byte(self) -> byte:
        return byte(self.get_and_increment())

    @type_parser(str)
    def parse_str(self) -> str:
        length = abs(self.parse_int(False))
        return self.get_and_increment(length, True).decode()

    @type_parser(int)
    def parse_int(self, optimized=True) -> int:
        if not optimized:
            return int.from_bytes(self.get_and_increment(4), 'little')
        if res := self.get_and_increment() == 255:
            return int.from_bytes(self.get_and_increment(4), 'little')
        else:
            return res

    @type_parser(short)
    def parse_short(self, optimized=True) -> short:
        if not optimized:
            return short.from_bytes(self.get_and_increment(2), 'little')
        if res := self.get_and_increment() == 255:
            return short.from_bytes(self.get_and_increment(2), 'little')
        else:
            return short(res)

    @type_parser(bytes)
    def parse_bytes(self, length):
        return self.get_and_increment(length, True)

    @type_parser(single)
    def parse_single(self):
        return single.fromhex(''.join(hex(i)[2:] for i in self.parse_bytes(4)))

    @type_parser(float)
    def parse_double(self):
        return float.fromhex(''.join(hex(i)[2:] for i in self.parse_bytes(8)))

    @type_parser(Dict[K, V])
    def parse_dict(self, parse_key: Callable[[], K], parse_value: Callable[[], V]) -> Mapping[K, V]:
        length = abs(self.parse_int(False))
        return {
            parse_key(): parse_value()
            for _ in range(length)
        }

    @property
    def current(self):
        return self.value[self.index]

    def get_and_increment(self, amount: int = 1, force_bytes=False) -> Union[int, bytes]:
        if amount == 1 and not force_bytes:
            res = self.current
        else:
            res = self.value[self.index:self.index + amount]
        self.index += amount
        return res

    def check(self):
        if crc32(self.value[:-4]) != self.checksum:
            raise SyntaxError('bad checksum')

    @property
    def checksum(self):
        return int.from_bytes(self.value[-4:], 'little')

    def parse_version(self):
        return tuple(self.parse_short(False) for _ in range(4))

    def parse_gen_settings(self):
        return {
            'terrain_segmentation': self.parse_byte(),
            'water': self.parse_byte(),
            'autoplace_controls': self.parse_dict(get_parser(str, self), partial(get_parser(bytes, self), 3)),
            'TODO': self.parse_bytes(2),
            'seed': self.parse_int(False),
            'width': self.parse_int(False),
            'height': self.parse_int(False),
            'starting_area': self.parse_byte(),
            'peaceful': self.parse_bool()
        }

    def parse_from_prototype(self, prototype: Mapping[str, type]):
        return {name: type_parsers[type_](self) for name, type_ in prototype.items()}

    def parse_steering(self):
        return {
            'default': self.parse_from_prototype(prototype_steering),
            'moving': self.parse_from_prototype(prototype_steering)
        }

    def parse_map_settings(self):
        return {
            'pollution': self.parse_from_prototype(prototype_pollution),
            'steering': self.parse_steering(),
            'enemy_evolution': self.parse_from_prototype(prototype_evolution),
            'enemy_expansion': self.parse_from_prototype(prototype_expansion),
            'path_finder': self.parse_from_prototype(prototype_pathfinder),
            'max_failed_behavior_count': self.parse_int(),
            'difficulty': self.parse_from_prototype(prototype_difficulty)
        }

    def get_component(self, name: str, parser: Callable[[], Any]):
        if name not in self.data:
            res = parser()
            self.data[name] = res
        return name, self.data[name]

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        yield self.get_component('version', self.parse_version)
        yield self.get_component('gen_settings', self.parse_gen_settings)
        yield self.get_component('map_settings', self.parse_map_settings)

    def __getitem__(self, item):
        return self.value[item]

    def __repr__(self):
        return f"ExchangeStringParser('{self.original}')"
