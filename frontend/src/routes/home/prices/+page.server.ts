import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices, supabase } }) => {
	const { data: staff, error: staffError } = await supabase
		.from('staff')
		.select('user_id, first_name, last_name, email');

	const { data: price_history, error } = await supabasePrices
		.from('price_history')
		.select('*,providers(*),loaded_prices(hash)')
		.order('status', { ascending: true })
		.order('created_at', { ascending: false });
	
	console.log('Price history data:', price_history);

	const staffMap = new Map(staff!.map((employee) => [employee.user_id, employee]));

	const enrichedPriceHistory = price_history!.map((priceEntry) => ({
		...priceEntry,
		user: staffMap.get(priceEntry.user_id) || null,
		provider_name: priceEntry.providers?.name || null
	}));

	return {
		price_history: enrichedPriceHistory ?? [],
		error: error
	};
};
