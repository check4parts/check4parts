import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices, supabase } }) => {
	const staff = new Promise<any[]>((resolve) => {
		supabase
			.from('staff')
			.select('user_id, first_name, last_name, email')
			.then(({ data, error }) => {
				if (error) {
					console.error(error);
					resolve([error]);
				} else {
					resolve(data);
				}
			});
	});

	const price_history = new Promise<any[]>((resolve) => {
		supabasePrices
			.from('price_history')
			.select('*,providers(*),loaded_prices(hash)')
			.not('loaded_id', 'is', null)
			.order('status', { ascending: true })
			.order('created_at', { ascending: false })
			.then(({ data, error }) => {
				if (error) {
					console.error(error);
					resolve([error]);
				} else {
					resolve(data);
				}
			});
	});
	return {
		price_history: price_history,
		staff: staff
	};
};
