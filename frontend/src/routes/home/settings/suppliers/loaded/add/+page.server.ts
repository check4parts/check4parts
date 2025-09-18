import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices: supabase } }) => {
	const [providersResponse, warehousesResponse, currenciesResponse, templateResponse] = await Promise.all([
		supabase.from('providers').select('*').order('name'),
		supabase.from('warehouses').select('*').order('name'),
		supabase.from('currencies').select('*'),
		supabase.from('provider_template').select('*')
	]);

	if (providersResponse.error) {
		console.error('Error fetching providers:', providersResponse.error);
		throw fail(500, { message: 'Failed to load providers.' });
	}

	if (warehousesResponse.error) {
		console.error('Error fetching warehouses:', warehousesResponse.error);
		throw fail(500, { message: 'Failed to load warehouses.' });
	}

	if (currenciesResponse.error) {
		console.error('Error fetching currencies:', currenciesResponse.error);
		throw fail(500, { message: 'Failed to load currencies.' });
	}

	if (templateResponse.error) {
		console.error('Error fetching template:', templateResponse.error);
		throw fail(500, { message: 'Failed to load template.' });
	}

	return {
		providers: providersResponse.data,
		warehouses: warehousesResponse.data,
		currencies: currenciesResponse.data,
		providerTemplates: templateResponse.data
	};
};
