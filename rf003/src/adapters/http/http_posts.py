



class RoutesAdapter(RoutesPort):
    async def get_or_create_route(self, origin: str, destination: str) -> Route:
        # 1. Search for an existing route.
        existing_route = await self._find_route_in_db(origin, destination)
        if existing_route:
            return existing_route
        else:
            # 2. If it doesn't exist, create a new one.
            new_route_data = Route(origin=origin, destination=destination)
            new_route = await self._create_route_in_db(new_route_data)
            return new_route