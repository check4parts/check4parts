import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals: { supabasePrices: supabase } }) => {
	const query = url.searchParams.get('q')?.trim();

	if (!query) {
		return {
			query: '',
			data: [],
			warehouses: [],
			fetchError: null
		};
	}

	const { data, error: fetchError } = await supabase
		.from('prices')
		.select('*, providers(*)')
		.eq('article', query)
		.limit(20);

	const provider_ids = data?.map((p) => p.provider_id);

	const { data: warehouses } = await supabase
		.from('warehouses')
		.select('id, name, short_name')
		.in('provider_id', provider_ids?.length ? provider_ids : []);

	return {
		query,
		data,
		warehouses,
		fetchError
	};
};
