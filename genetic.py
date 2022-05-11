from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string, re, random

class Decoder:
    def __init__(self, global_text, encoded_text, key_lenght=14):
        self.global_text = global_text
        self.encoded_text = encoded_text
        self.key_lenght = key_lenght
        self.clean_encoded_text = self.__process_text(encoded_text)
        self.dictionary = self.__create_dictionary(global_text)
        self.n_encoded_token = len(self.clean_encoded_text.split())

    def decode(self):
        key = self.find_key()
        keyidx = 0
        plain_text = ''
        for c in self.encoded_text:
            if c.isalpha():
                if c.isupper():
                    plain_text += chr(((ord(c) - ord(key[keyidx % len(key)])) % 26) + 65)
                else:
                    plain_text += chr(((ord(c) - ord(key[keyidx % len(key)].lower())) % 26) + 97)
                keyidx += 1
            else:
                plain_text += c
        return plain_text

    def find_key(self):
        initial_population = self.__generate_population(100)
        population, max_fit = self.__calculate_fitness(initial_population)
        n = 0
        while  max_fit < self.n_encoded_token:
            n += 1
            # print(f'score: {self.__get_fittest_chromosome(population)[1]} gen: {n}')
            r, h = self.__selection(population)
            r = self.__crossover(r, len(r))
            population = list(r + h)
            population, max_fit = self.__calculate_fitness(population)
            population = self.__mutation(population)
        fittest_chromosome = self.__get_fittest_chromosome(population)
        print(f'Key: {fittest_chromosome[0].lower()} found in {n}th generation\n')
        return fittest_chromosome[0]

    def __selection(self, population):
        sorted_population = sorted(population, key=lambda pair: pair[1])
        remain = sorted_population[:int(len(population) * 0.6)]
        heros = sorted_population[-(len(population) -int(len(population) * 0.6)):]
        return remain, heros

    def __crossover(self, individuals, pop_size):
        next_generation = []
        random.shuffle(individuals)
        for i in range(pop_size // 2):
            a = individuals.pop()
            b = individuals.pop()
            c1, c2 = self.__crossover_util(a, b)
            if self.__calculate_fitness_for_key(c1[0]) < a[1]:
                c1 = a
            if self.__calculate_fitness_for_key(c2[0]) < b[1]:
                c2 = b
            next_generation.append(c1)
            next_generation.append(c2)
        return next_generation
        
    def __crossover_util(self, par1, par2):
        p1 = list(par1[0])
        p2 = list(par2[0])
        x = random.randint(0, self.key_lenght - 1)
        for i in range(x, self.key_lenght):
            p1[i], p2[i] = p2[i], p1[i]
        child1 = ''.join(p1)
        child2 = ''.join(p2)
        return (child1, par1[1]), (child2, par2[1]) 

    def __mutation(self, population):
        new_population = []
        for x in population:
            if random.random() < 0.2:
                old = x[:]
                p = random.randint(0, self.key_lenght -1)
                x = (x[0][:p] + random.choice(string.ascii_uppercase) + x[0][p + 1:], x[1])
                newfit = self.__calculate_fitness_for_key(x[0])
                x = (x[0], newfit)
                if newfit < self.__calculate_fitness_for_key(old[0]):
                    x = old
            new_population.append(x)
        return new_population
    
    def __get_fittest_chromosome(self, population):
        max_fit = -1
        max_chrom = ''
        for chromosome in population:
            if chromosome[1] > max_fit:
                max_fit = chromosome[1]
                max_chrom = chromosome
        return max_chrom
    
    def __generate_population(self, population_size):
        population = []
        for i in range(population_size):
            newChromosome = ''.join(random.choice(string.ascii_uppercase) for i in range(self.key_lenght))
            population.append((newChromosome, 0))
        return population

    def __calculate_fitness_for_key(self, key):
        fit = 0
        for token in self.__decrypt(key, self.clean_encoded_text):
            if token in self.dictionary:
                fit += 1
        return fit

    def __calculate_fitness(self, population):            
        max_fit = -1
        for i ,p in enumerate(population):
            fit = self.__calculate_fitness_for_key(p[0])
            population[i] = (p[0], fit)
            if fit > max_fit:
                max_fit = fit
        return population, max_fit
        
    def __decrypt(self,key, cipher_text):
        key = key.upper()
        keylen = len(key)
        keyidx = 0
        plain_text = []
        cipher_text = cipher_text.upper()
        for w in cipher_text.split():
            token = ''
            for i in range(0, len(w)):
                token += chr(((ord(w[i]) - ord(key[keyidx])) % 26) + 65)
                keyidx += 1
                if keyidx > keylen - 1:
                    keyidx = 0
            plain_text.append(token)
        return plain_text
        
    def __create_dictionary(self, text):
        text = self.__process_text(text)
        # Remove stopwords
        stop_words = set(stopwords.words("english"))
        tokens = word_tokenize(text)
        dictionary = [w for w in tokens if w not in stop_words]

        return set(dictionary)
    
    def __process_text(self, text):
        # UpperCase
        text = text.upper()

        text = re.sub('[^A-Z]+', ' ', text)

        # Remove whitespaces
        text = " ".join(text.split())

        return text

encodedText=open('encoded_text.txt').read()
globalText=open('global_text.txt').read()

d= Decoder(globalText,encodedText, key_lenght=14)
decodedText=d.decode()