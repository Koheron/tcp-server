/// Generated by Devgen 
/// DO NOT EDIT
///
/// (c) Koheron

#ifndef __DEVICES_TABLE_HPP__
#define __DEVICES_TABLE_HPP__

#include <array>
#include <tuple>
#include <memory>

#include <core/string_utils.hpp>
#include <core/meta_utils.hpp>

using device_id = std::size_t;

class NoDevice;
class KServer;
{% for device in devices %}
class {{ device.objects[0]["type"] }};
{% endfor -%}

constexpr device_id device_num = {{ devices|length + 2 }};

constexpr auto devices_names = kserver::make_array(
    kserver::str_const("NoDevice"),
    kserver::str_const("KServer"),
{%- for device in devices -%}
{% if not loop.last %}
    kserver::str_const("{{ device.objects[0]['type'] }}"),
{%- else %}
    kserver::str_const("{{ device.objects[0]['type'] }}")
{%- endif %}
{%- endfor %}
);

static_assert(std::tuple_size<decltype(devices_names)>::value == device_num, "");

// Devices are store as unique_ptr ensuring single
// instantiation of each device.

using devices_tuple_t = std::tuple<
{%- for device in devices -%}
{% if not loop.last -%}
 std::unique_ptr<{{ device.objects[0]['type'] }}>,
{%- else -%}
 std::unique_ptr<{{ device.objects[0]['type'] }}>
{%- endif -%}
{%- endfor -%}
>;

static_assert(std::tuple_size<devices_tuple_t>::value == device_num - 2, "");

// Device id from device type

template<class Dev> constexpr device_id dev_id_of;
template<> constexpr device_id dev_id_of<NoDevice> = 0;
template<> constexpr device_id dev_id_of<KServer> = 1;

template<class Dev>
constexpr device_id dev_id_of
	= Index_v<std::unique_ptr<Dev>, devices_tuple_t> + 2;

// Device type from device id

template<device_id dev>
using device_t = std::remove_reference_t<
					decltype(*std::get<dev - 2>(std::declval<devices_tuple_t>()))>;

#endif // __DEVICES_TABLE_HPP__
