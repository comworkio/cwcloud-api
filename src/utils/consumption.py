import json

from urllib.error import HTTPError
from datetime import datetime

from entities.Consumption import Consumption
from entities.Instance import Instance

from utils.common import is_false
from utils.date import parse_date
from utils.encoder import AlchemyEncoder
from utils.provider import  get_provider_instance_price

def getConsumptionsByDate(from_date, to_date, id, f_get_consumptions, f_get_instance_id, f_get_user_id):
    pfrom_date = parse_date(from_date)
    pto_date = parse_date(to_date)

    from_date_iso = pfrom_date['value']
    if is_false(pfrom_date['status']):
        raise HTTPError("bad_date_aaaammdd", 400, "Bad date format : {}".format(from_date_iso), hdrs = {"i18n_code": "bad_date_aaaammdd"}, fp = None)

    to_date_iso = pto_date['value']
    if is_false(pto_date['status']):
        raise HTTPError("bad_date_aaaammdd", 400, "Bad date format : {}".format(to_date_iso), hdrs = {"i18n_code": "bad_date_aaaammdd"}, fp = None)

    consumptions = f_get_consumptions(id)
    filtered_consumptions = []
    for consumption in consumptions:
        from_date_consumption = datetime.fromisoformat(str(consumption.from_date))
        to_date_consumption = datetime.fromisoformat(str(consumption.to_date))
        new_from_date = None
        new_to_date = None

        if from_date_consumption <= from_date_iso and to_date_consumption >= from_date_iso:
            new_from_date = from_date_iso
            new_to_date = to_date_iso if to_date_consumption >= to_date_iso else to_date_consumption
        elif from_date_consumption >= from_date_iso and from_date_consumption <= to_date_iso:
            new_from_date = from_date_consumption
            new_to_date = to_date_consumption if to_date_consumption <= to_date_iso else to_date_iso

        if new_from_date and new_to_date:
            usage = new_to_date.timestamp() - new_from_date.timestamp()
            usage_hour = round(usage/3600, 4)
            total_price = round(float(consumption.instance_price) * float(usage_hour), 4)
            instance_json = json.loads(json.dumps(consumption.instance, cls = AlchemyEncoder))
            created_consumption = {
                "instance_id": f_get_instance_id(id, consumption),
                "user_id": f_get_user_id(id, consumption),
                "instance": instance_json,
                "usage": usage_hour,
                "instance_price": consumption.instance_price,
                "total_price": total_price,
                "from_date": new_from_date.isoformat(),
                "to_date": new_to_date.isoformat()
            }

            filtered_consumptions.append(created_consumption)

    return filtered_consumptions

def getInstanceConsumptionsByDate(from_date, to_date, instance_id, db):
    return getConsumptionsByDate(
        from_date,
        to_date,
        instance_id,
        lambda id: Consumption.getInstanceConsumptions(id, db),
        lambda id, consumption: consumption.instance_id.id,
        lambda id, consumption: consumption.user_id
    )

def getUserConsumptionsByDate(from_date, to_date, user_id, db):
    return getConsumptionsByDate(
        from_date,
        to_date,
        user_id,
        lambda id: Consumption.getUserAllConsumptions(id, db),
        lambda id, consumption: consumption.instance.id,
        lambda id, consumption: id
    )

def compute_usage(compared_date, from_date, activated_at):
    return compared_date - from_date if from_date > activated_at else compared_date - activated_at

def get_instance_usage(current_date, activated_at, dateFrom, dateTo):
    now_date = datetime.fromisoformat(str(current_date)).timestamp()
    activated_at = datetime.fromisoformat(str(activated_at)).timestamp()
    from_date = datetime.fromisoformat(str(dateFrom)).timestamp()
    to_date = datetime.fromisoformat(str(dateTo)).timestamp()
    usage = 0

    if to_date < activated_at:
     return 0

    usage = compute_usage(to_date, from_date, activated_at) if to_date < now_date else compute_usage(now_date, from_date, activated_at)
    usage_hour = round(usage/3600, 4)
    return usage_hour

def generate_instance_consumption(user_id, instance, dateFrom, dateTo, save, db):
    current_date = datetime.now().isoformat()
    activated_at = instance.modification_date
    activated_at_iso = datetime.fromisoformat(str(activated_at))

    new_from_date = None
    if activated_at_iso <= dateFrom:
        new_from_date = dateFrom
    elif activated_at_iso <= dateTo:
        new_from_date = activated_at_iso

    if not new_from_date:
        return None

    usage_hour = get_instance_usage(current_date, activated_at, dateFrom, dateTo)
    instance_price = get_provider_instance_price(instance.provider, instance.region, instance.zone, instance.type)
    total_price = round(float(instance_price) * float(usage_hour), 4)
    instance_json = json.loads(json.dumps(instance, cls = AlchemyEncoder))

    created_consumption = {
        "instance_id": instance.id,
        "user_id": user_id,
        "instance": instance_json,
        "usage": usage_hour,
        "instance_price": instance_price,
        "total_price": total_price,
        "from_date": new_from_date.isoformat(),
        "to_date": dateTo.isoformat()
    }

    if save:
        new_consumption = Consumption()
        new_consumption.instance_id = instance.id
        new_consumption.usage = usage_hour
        new_consumption.instance_price = instance_price
        new_consumption.total_price = total_price
        new_consumption.from_date = activated_at
        new_consumption.to_date = current_date
        new_consumption.user_id = user_id
        new_consumption.save(db)
        Instance.updateModificationDate(instance.id, current_date, db)

    return created_consumption

def generate_user_consumptions(user_id, from_date, to_date, db):
    instances = Instance.getAllUserInstances(user_id, db)
    consumptions = []
    for instance in instances:
        if instance.status == 'active':
            consumption = generate_instance_consumption(user_id, instance, from_date, to_date, False, db)
            if consumption:
                consumptions.append(consumption)

    return consumptions
