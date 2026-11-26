"""Moduł zwrotów (przykładowa aplikacja do testów dokumentacji)."""
from datetime import date, timedelta

from flask import Blueprint, abort, request

from .auth import current_user, require_role
from .i18n import t

bp = Blueprint("returns", __name__, url_prefix="/orders/<int:order_id>/returns")

MAX_DAYS = 30            # Returns:MaxDays w appsettings, domyślnie 30
MAX_PHOTOS = 3
MAX_PHOTO_MB = 5
REASONS = ("damaged", "not_as_described", "other")


@bp.route("/new", methods=["POST"])
@require_role("customer")
def create_return(order_id: int):
    order = current_user().orders.get(order_id) or abort(404)
    if order.status != "delivered":
        return {"error": t("returns.error.not_delivered")}, 400
    if date.today() - order.delivered_on > timedelta(days=MAX_DAYS):
        return {"error": t("returns.error.too_late")}, 400
    form = request.form
    if form.get("reason") not in REASONS:
        return {"error": t("returns.error.reason_required")}, 400
    if len(form.get("comment", "")) > 500:
        return {"error": t("returns.error.comment_too_long")}, 400
    photos = request.files.getlist("photos")
    if len(photos) > MAX_PHOTOS or any(p.content_length > MAX_PHOTO_MB * 1024 * 1024 for p in photos):
        return {"error": t("returns.error.photos")}, 400
    order.create_return(reason=form["reason"], comment=form.get("comment"), photos=photos,
                        status="pending_approval")
    return {"message": t("returns.created")}, 201


@bp.route("/<int:return_id>/approve", methods=["POST"])
@require_role("returns_manager")
def approve_return(order_id: int, return_id: int):
    # TODO: częściowa akceptacja (nieukończone, ukryte w interfejsie)
    ...
