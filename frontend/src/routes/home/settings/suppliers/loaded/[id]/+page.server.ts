import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices }, params }) => {
	const history_id = params.id;
	const { data: price_history, error: historyError } = await supabasePrices
		.from('price_history')
		.select('*, providers(*),loaded_prices(*)')
		.eq('id', history_id)
		.single();

	if (price_history.status === 'actual' || price_history.status === 'cloned') {
		const price = new Promise<any[]>((resolve, reject) => {
			supabasePrices
				.from('prices')
				.select('*')
				.eq('loaded_id', price_history.loaded_id)
				.limit(100)
				.then(({ data, error }) => {
					if (error) resolve([]);
					else resolve(data);
				});
		});

		const { data: count } = await supabasePrices
			.from('loaded_prices_with_references')
			.select('price_rows_count,reference_count')
			.eq('loaded_price_id', price_history.loaded_id)
			.single();

		const { data: warehouses } = await supabasePrices.from('warehouses').select('*').order('name');

		return {
			price: price,
			count: count?.price_rows_count || 0,
			reference_count: count?.reference_count || 0,
			price_history: price_history || [],
			warehouses: warehouses || []
		};
	}
	return {
		price: Promise.resolve([]),
		price_history: price_history || [],
		warehouses: [],
		count: 0,
		reference_count: 0
	};
};
