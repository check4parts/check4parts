import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
  depends('supabase:db:company_provider');

  const { data, error } = await supabase
    .from('company_provider')
    .select('*,providers(*)');

  if (error) {
    console.error('Error fetching suppliers:', error);
    throw new Error('Failed to load suppliers.');
  }

  return { suppliers: data ?? [] };
};
