import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async (
	{ depends, locals: { supabase }, params },
) => {
	depends("supabase:db:staff");
	const userId = params.id;
	const { data: user } = await supabase
		.from("staff")
		.select("*,roles(name),trading_points(*)")
		.eq("id", userId).single();

	depends("supabase:db:roles");
	const { data: roles } = await supabase.from("roles").select("*").order(
		"name",
	);

	depends("supabase:db:trading-points");
	const { data: points } = await supabase.from("trading_points").select("*")
		.order("name");
	return { user: user ?? {}, roles: roles ?? [], points: points ?? [] };
};
