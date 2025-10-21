import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:clients');
	depends('supabase:db:client_types');

	const [clientsResponse, clientTypesResponse] = await Promise.all([
		supabase.from('clients').select('*, cars(*)'),
		supabase.from('client_types').select('*')
	]);

	if (clientsResponse.error) {
		console.error('Помилка завантаження клієнтів:', clientsResponse.error);
		throw error(500, {
			message: 'Не вдалося завантажити клієнтів.'
		});
	}

	if (clientTypesResponse.error) {
		console.error('Помилка завантаження типів клієнтів:', clientTypesResponse.error);
		throw error(500, {
			message: 'Не вдалося завантажити типи клієнтів.'
		});
	}

	return {
		clients: clientsResponse.data ?? [],
		clientTypes: clientTypesResponse.data ?? []
	};
};