import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices: supabase } }) => {
	const [providersResponse, warehousesResponse] = await Promise.all([
		supabase.from('providers').select('*').order('name'),
		supabase.from('warehouses').select('*').order('name')
	]);

	if (providersResponse.error) {
		console.error('Error fetching providers:', providersResponse.error);
		throw fail(500, { message: 'Failed to load providers.' });
	}

	if (warehousesResponse.error) {
		console.error('Error fetching warehouses:', warehousesResponse.error);
		throw fail(500, { message: 'Failed to load warehouses.' });
	}

	return {
		providers: providersResponse.data,
		warehouses: warehousesResponse.data
	};
};
